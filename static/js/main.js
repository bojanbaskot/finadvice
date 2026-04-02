document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    document.querySelectorAll('.alert.alert-dismissible').forEach(function(el) {
      bootstrap.Alert.getOrCreateInstance(el).close();
    });
  }, 5000);
});
