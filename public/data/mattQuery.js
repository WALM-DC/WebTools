function addZero(n) {return (n < 10)? '00' + n : (n < 100)? '0' + n : '' + n;}
const tabs = {
    'XML Liste': "https://ig-creator.xxxlgroup.com/idm/XMLLister/xmlListerIndex.html",
    'XML Liste + Zielmarkt': "https://ig-creator.xxxlgroup.com/idm/XMLLister/xmlListerCountryIndex.html",
    'XML Checker': "https://ig-creator.xxxlgroup.com/idm/XMLLister/xmlChecker.html",
    'Registry Liste': "https://ig-creator.xxxlgroup.com/idm/XMLLister/xmlRegistryLister.html",
    '3D Modell&uuml;bersicht': "https://ig-creator.xxxlgroup.com/idm/XMLLister/3DModelOverview.html",
    '3D Modell-Details': "https://ig-creator.xxxlgroup.com/idm/XMLLister/3DModelDetails.html",
    'Stoff Zusammensetzungen': "https://ig-creator.xxxlgroup.com/idm/XMLLister/igAssetList.html",
    'PIM API Checker': "https://ig-creator.xxxlgroup.com/idm/XMLLister/PIMApiChecker.html",
    'VKP & Aktion': "https://ig-creator.xxxlgroup.com/idm/XMLLister/VKPundAktion.html",
    'Link Sammlung': "https://ig-creator.xxxlgroup.com/idm/XMLLister/LinkSammlung.html"
};
function injectTabs(){
    const tabListDiv = document.createElement("div");
    tabListDiv.id = "tabList";
    tabListDiv.className = "tabList";
    document.getElementById('topDiv').appendChild(tabListDiv);
    Object.entries(tabs).forEach(([name, link]) => {
        const tabA = document.createElement("a");
        tabA.className = "tab";
        tabA.href = link;
        tabA.innerHTML = `<h2>${name}</h2>`;
        document.getElementById('tabList').appendChild(tabA);
    });
    $('.tab[href="'+window.location.href+'"]').addClass('active');
}
function removeHighlights() {
    $("mark").each(function() {
        $(this).replaceWith($(this).text());
    });
}
function highlightOccurrences(searchString) {
    removeHighlights();    
    const regex = new RegExp(searchString, "gi");
    $("body *").contents().each(function() {
        if (this.nodeType === 3) { // Only process text nodes
            const text = $(this).text();
            const highlightedText = text.replace(regex, function(match) {
                return `<mark>${match}</mark>`;
            });
            $(this).replaceWith(highlightedText);
        }
    });
}
function filterTable() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toLowerCase();
    table = document.getElementById("myTable");
    tr = table.getElementsByTagName("tr");

    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td");
        for (var j = 0; j < td.length; j++) {
            txtValue = td[j].textContent || td[j].innerText;
            if (txtValue.toLowerCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
                break;
            } else {
                tr[i].style.display = "none";
            }
        }
    }
    countColumns();
    if(filter.length > 0){
        highlightOccurrences(filter);
    }
}