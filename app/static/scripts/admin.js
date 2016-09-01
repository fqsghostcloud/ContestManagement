
function gaoActiveLink(item) {
  var cur_location = String(window.location);
  cur_location = cur_location.split('?')[0];
  $(item).each(function() {
    if ($($(this))[0].href.split('?')[0] == String(cur_location)) {
      $(this).parent().addClass('active');
      var $pa = $(this).parent().parent().parent();
      if ($pa.hasClass('treeview')) {
          $pa.addClass('active');
      }
      $(this).click(function() {
          return false;
      });
    } else {
      $(this).parent().removeClass('active');
    }
  });
}
