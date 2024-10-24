<script>
import { refreshIntervalInMs } from "@common/settings";

export default {
  methods: {
    setupAutoRefresh() {
      (function loop(context) {
        setTimeout(async () => {
          // Don't refresh if the page is hidden
          if (!document.hidden) {
            try {
              await context.refresh();
            } catch (error) {
              // Interrupt loop on error, except server errors
              if (!error?.response?.status || error.response.status < 500) {
                throw error;
              }
            }
          }
          loop(context);
        }, refreshIntervalInMs);
      })(this);
    },
  },
};
</script>
