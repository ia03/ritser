$('document').ready(function(){
    document.getElementById('id_content_type').setAttribute('onchange', 'ontypchg();');
});

function ontypchg()
{
    var label = $("label[for='id_object_id']");
    var ctype = document.getElementById('id_content_type').value;
    if (ctype == 4)
    {
        label.html('Name:');
    } else if (ctype == 5)
    {
        label.html('Username:');
    } else
    {
        label.html('ID:');
    }
}