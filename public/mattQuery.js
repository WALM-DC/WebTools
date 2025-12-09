function addZero(n) {return (n < 10)? '00' + n : (n < 100)? '0' + n : '' + n;}
function injectTabs(){
    $.get('https://walm-dc.github.io/WebTools/public/tabs.html', function(data){
        $('#topDiv').html(data);
    });
}