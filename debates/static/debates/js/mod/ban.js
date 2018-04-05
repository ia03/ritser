var picker = new Pikaday({ field: document.getElementById('id_bandate'), format: 'MM/DD/YYYY' });
jQuery(document).ready(function () {
   $("#id_terminate").click(function () {
      $('#id_bandate').attr("disabled", $(this).is(":checked"));
      $('#id_bannote').attr("disabled", $(this).is(":checked"));
   });
});