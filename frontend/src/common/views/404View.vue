<template>
  <div class="container">
    <div class="content">
      <v-icon x-large>$vuetify.icons.eurydiceLogo</v-icon>
      <h1 class="item" margin="20px">Erreur 404</h1>
      <p class="item">Cette page n'existe pas.</p>
      <a class="item" href="/">Retour à l'accueil</a>
    </div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  height: 600px;
}

.content {
  margin: auto;
  text-align: center;
}

.item {
  margin: 15px;
}
</style>
