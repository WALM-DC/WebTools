function addZero(n) {return (n < 10)? '00' + n : (n < 100)? '0' + n : '' + n;}
function injectTabs(){
    $.get('https://walm-dc.github.io/WebTools/public/tabs.html', function(data){
        $('#topDiv').html(data);
        $('[link="'+window.location.href+'"]').addClass('active');
    });
}
function relinkToPage(this){
    var link = $(this).attr('link');
    window.location.href = link;
}
