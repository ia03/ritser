var gdprconsent = document.getElementById('id_gdprconsent');
var email = document.getElementById('id_email');
window.onload = function ()
{
    gdprconsent.disabled = true;
};
email.onchange = function()
{
    if (this.value.length > 0)
    {
        gdprconsent.disabled = false;
    } else {
        gdprconsent.disabled = true;
    }
};