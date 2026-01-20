import json
from datetime import datetime
from hashlib import md5

from django.conf import settings
from django.db.models import Model, QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.aliases import StrPromise
from rest_framework import pagination
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.pagination import CursorPagination
from rest_framework.request import Request
from rest_framework.views import APIView

from eurydice.common.api.pagination.dataclasses import Link, PageIdentifier, Query, Session


class PageGone(APIException):
    """Exception raised when the DBTrimmer removed a page that was being explored."""

    status_code = 410
    default_detail = "The requested page does not exist anymore"
    default_code = "page_gone"


class EurydiceSessionPaginationWithoutOpenapi(CursorPagination):
    """
    Custom pagination class, optimized for performances, without OpenAPI definitions.

    This pagination class provides the following functionalities:
    - previous/current/next page identifiers: they can be used to navigate through the
      database consistently (pages will always contain the same items refreshed every
      query, independently from new items in the database);
    - a new items detection mechanism: a boolean will indicate if new items are
      available in the database;
    - a count feature: the total amount of items in the database will be displayed in
      requests.
    """

    no_page_size_message: StrPromise = _("Missing page size query parameter")
    params_message: StrPromise = _("Query parameters that started the pagination were altered")
    invalid_page_identifier_message: StrPromise = _("Invalid page identifier")
    invalid_page_message: StrPromise = _("Query parameters resulted in an invalid page number")
    page_or_from_message: StrPromise = _("Either page or from must be present (and not both)")
    invalid_delta_message: StrPromise = _("Invalid page delta")

    from_query_param: str = "from"
    from_query_description: StrPromise = _("Page identifier from which to apply a delta.")

    page_query_param: str = "page"
    page_query_description: StrPromise = _("Page identifier within the paginated result set.")

    delta_query_param: str = "delta"
    delta_query_description: StrPromise = _("Delta relative to the given page.")

    max_page_size: int = settings.MAX_PAGE_SIZE
    page_size_query_param: str = "page_size"

    ordering: str | list[str] | tuple[str, ...] = ("-created_at", "id")

    def paginate_queryset(self, queryset: QuerySet, request: Request, view: APIView | None = None) -> list | None:
        """Gather the information needed to build the API response."""

        self.query = self.parse_query_params(request)

        # Build the `new_items` field
        new_first_item = self.fetch_leading_item_position(queryset, reverse=False)
        self.first_item = None
        if self.query.session and self.query.session.first_item:
            self.first_item = self.query.session.first_item
            self.new_items = self.query.session.first_item != new_first_item
        else:
            self.first_item = new_first_item
            self.new_items = False

        # Set the `paginated_at` field if needed
        if self.query.session:
            self.paginated_at = self.query.session.paginated_at
        else:
            self.paginated_at = timezone.now()

        # "Freeze" the queryset if applicable
        if self.query.session and self.new_items:
            queryset = queryset.filter(**{self.ordering[0].lstrip("-") + "__lte": self.query.session.first_item})

        # Check if a database trimming happened
        self.new_last_item = self.fetch_leading_item_position(queryset, reverse=True)
        if self.query.session:
            self.deleted_items = self.query.session.last_item != self.new_last_item
        else:
            self.deleted_items = False

        # Build the `count` field (update it if there was a trimming)
        if self.query.session is None or self.deleted_items:
            self.items_count = queryset.values("id").count()
        else:
            self.items_count = self.query.session.items_count

        # Build the `results` field
        super().paginate_queryset(queryset, request, view=view)

        # Check if the page is empty and build the `pages` field
        if self.page:
            self.page_identifiers = self.build_page_identifiers(self.build_session())
        else:
            self.handle_empty_page(request)
            self.page_identifiers = self.build_page_identifiers(None)

        # Django REST Framework expects the page to be returned here
        return self.page

    def parse_navigation_params(self, request: Request) -> tuple[Session, int] | None:
        """Load the `page`, `from` and `delta` query parameters."""

        page_given = self.page_query_param in request.query_params
        from_given = self.from_query_param in request.query_params
        delta_given = self.delta_query_param in request.query_params

        if not page_given and not from_given and not delta_given:
            return None

        if from_given == page_given:
            raise ValidationError(self.page_or_from_message)

        try:
            delta = int(request.query_params[self.delta_query_param])
        except ValueError:
            raise ValidationError(self.invalid_delta_message)
        except KeyError:
            delta = 0

        page_param = self.page_query_param if page_given else self.from_query_param

        try:
            page_identifier = PageIdentifier.unpack(request.query_params[page_param])
        except (TypeError, ValueError):
            raise ValidationError(self.invalid_page_identifier_message)

        return page_identifier.session, delta + page_identifier.offset

    def parse_query_params(self, request: Request) -> Query:
        """Parse all query parameters and accordingly build a Query object."""

        session_and_delta = self.parse_navigation_params(request)
        if session_and_delta:
            session, delta = session_and_delta

        self.query_params_hash = self.compute_query_params_hash(request)
        if session_and_delta and self.query_params_hash != session.query_params_hash:
            raise ValidationError(self.params_message)

        queried_page = (session.page_number + delta) if session_and_delta else 1
        if queried_page < 1:
            raise ValidationError(self.invalid_page_message)

        return Query(queried_page=queried_page, session=session if session_and_delta else None)

    def get_optimized_link(self) -> Link:
        """
        Get a Link pointing to the current page.

        This method could simply always return `self.link`, but in some cases
        `self.link` has a position set to None, meaning the current page was accessed
        in a LIMIT/OFFSET fashion (see Links' docstring).

        If it's the case, we do not want to keep this link (too slow for the
        database), so we rewrite it as a *reversed* link, with a position equal to
        the database row *just after* the current page.

        Note that this optimization is only possible if the last item of the current
        page and the first item of the next one have different positions. This should
        always be the case, but the edge case where it's not is handled regardless.
        """

        if (
            self.link.position is None
            and self.page
            and self.has_next
            and self.next_position != self._get_position_from_instance(self.page[-1], self.ordering)
        ):
            return Link(offset=0, reverse=True, position=self.next_position)  # type: ignore # noqa: E501

        return self.link

    def build_link_for_query(self) -> Link:
        """
        Build a Link that will be used by the parent to query the current page.

        This method uses the links embedded in the session query parameter to build
        fast links to nearby pages.

        If there isn't any session query parameter, or if a database trimming happened
        (invalidating reverse cursor-style links), this method falls back to classic
        OFFSET/LIMIT pagination.
        """

        if self.page_size is None:
            raise ValidationError(self.no_page_size_message)  # pragma: no cover

        # Handle queries without session (basic OFFSET/LIMIT)
        offset_limit_link = Link((self.query.queried_page - 1) * self.page_size)
        if self.query.session is None:
            return offset_limit_link

        # Calculate the queried page delta from the session's previous page
        delta = self.query.queried_page - self.query.session.page_number

        # If requested, retrieve a previous page using the session's previous_link
        if delta < 0:
            if self.query.session.previous_link is None or self.deleted_items:
                return offset_limit_link

            return self.query.session.previous_link.with_offset((-delta - 1) * self.page_size)

        # If requested, retrieve a next page using the session's next_link
        if delta > 0:
            if self.query.session.next_link is None:
                return offset_limit_link

            return self.query.session.next_link.with_offset((delta - 1) * self.page_size)

        # If requested, retrieve the current page using the session's current_link
        if self.deleted_items:
            return offset_limit_link

        return self.query.session.current_link

    def build_session(self) -> Session:
        """
        Build the `session` field that will be returned in the API response.

        A session consists of eight elements that will be used by future queries:
        - previous, current and next links: used to quickly access nearby pages
        - the current page number: used to interpret page numbers relative to the
          aforementioned links
        - the items count: used to know how many items were in the database when the
          session began
        - first and last items: used to know if new items were added to the database
          since the session began, or if items were trimmed
        - a hash of query parameters : to avoid accidental changes to these params
        - the moment when the session was created: for informative purposes
        """

        return Session(
            previous_link=self.get_previous_link(),  # type: ignore
            current_link=self.get_optimized_link(),
            next_link=self.get_next_link(),  # type: ignore
            page_number=self.query.queried_page,
            items_count=self.items_count,
            first_item=self.first_item,
            last_item=self.new_last_item,
            query_params_hash=self.query_params_hash,
            paginated_at=self.paginated_at,
        )

    def build_page_identifiers(self, session: Session | None) -> dict[str, str | None]:
        """Create from 0 to 3 navigation links, to be included in the API response."""

        if session is None or self.page_size is None:
            return {"previous": None, "current": None, "next": None}

        pages = {
            "previous": -1,
            "current": 0,
            "next": 1,
        }

        result: dict[str, str | None] = {}
        for page_name, offset in pages.items():
            effective_offset = (session.page_number + offset - 1) * self.page_size
            if effective_offset < 0 or effective_offset >= session.items_count:
                result[page_name] = None
            else:
                result[page_name] = PageIdentifier(session, offset).pack()

        return result

    def handle_empty_page(self, request: Request) -> None:
        """Handle the fact that query parameters led to an empty page."""

        page_given = self.page_query_param in request.query_params
        from_given = self.from_query_param in request.query_params
        delta_given = self.delta_query_param in request.query_params

        if not page_given and not from_given and not delta_given:
            return

        if delta_given:
            raise NotFound("The requested page does not exist")

        raise PageGone("The requested page was too old and was trimmed")

    def compute_query_params_hash(self, request: Request) -> bytes:
        """Hash query params to ensure they stay the same across session pages."""

        # use .copy() to get a mutable version
        # https://docs.djangoproject.com/en/4.2/ref/request-response/#django.http.QueryDict
        query_params = request.query_params.copy()

        query_params.pop(self.page_query_param, None)
        query_params.pop(self.delta_query_param, None)
        query_params.pop(self.from_query_param, None)

        query_params_json = json.dumps(dict(query_params.lists()), sort_keys=True)

        return md5(query_params_json.encode("utf-8")).digest()[:4]  # nosec

    def fetch_leading_item_position(self, queryset: QuerySet, reverse: bool) -> datetime | None:
        """Perform a query to find the position of either the first or the last item."""

        ordering = self.ordering
        if reverse:
            ordering = pagination._reverse_ordering(ordering)

        latest_item = queryset.order_by(*ordering).first()

        if latest_item:
            return self._get_position_from_instance(latest_item, ordering)

        return None

    def _get_position_from_instance(  # type: ignore
        self,
        instance: Model,
        ordering: str | list[str] | tuple[str, ...],
    ) -> datetime:
        """Override parent's position retrieval to get dates instead of strings."""

        return getattr(instance, ordering[0].lstrip("-"))

    def get_html_context(self) -> "pagination.HtmlContext":  # pragma: no cover
        """Build previous and next URLs."""

        raise NotImplementedError

    def encode_cursor(self, cursor: Link) -> Link:  # type: ignore
        """
        Short-circuited.

        This method was used in the parent CursorPagination implementation to embed
        the given cursor inside a full URL. This behavior isn't suitable anymore,
        because we now embed cursors inside the session part of the API response.
        """

        return cursor

    def decode_cursor(self, _: Request) -> Link:  # type: ignore
        """
        Short-circuited.

        This method was used in the parent CursorPagination implementation to extract
        the given cursor from a full URL. This behavior isn't suitable anymore,
        because we now extract cursors from the session query parameter.
        """

        return self.build_link_for_query()

    @property
    def link(self) -> Link:
        """
        Alias for the `self.cursor` attribute.

        In this implementation, several terms were adapted and renamed for coherence
        purposes:
          - what users call a "cursor" is a "session" in this implementation;
          - what the parent implementation calls a "cursor" is a "link" in this
            implementation.
        """

        return Link(*self.cursor)  # type: ignore
