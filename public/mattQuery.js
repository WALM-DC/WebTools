function addZero(n) {return (n < 10)? '00' + n : (n < 100)? '0' + n : '' + n;}
const tabs = {
    'XML Liste': "https://ig-creator.xxxlgroup.com/idm/XMLLister/xmlListerIndex.html",
    'XML Liste + Country': "https://ig-creator.xxxlgroup.com/idm/XMLLister/xmlListerCountryIndex.html",
    'XML Checker': "https://ig-creator.xxxlgroup.com/idm/XMLLister/xmlChecker_v3.html",
    'Registry Liste': "https://ig-creator.xxxlgroup.com/idm/XMLLister/xmlRegistryLister.html",
    '3D Modell&uuml;bersicht': "https://ig-creator.xxxlgroup.com/idm/XMLLister/3DModelOverview_V2.html",
    '3D Modell-Details': "https://walm-dc.github.io/WebTools/public/3DModelDetails.html",
    'Link Sammlung': "https://walm-dc.github.io/WebTools/public/LinkSammlung.html"
};
function injectTabs(){
    const tabListDiv = document.createElement("div");
    tabListDiv.id = "tabList";
    tabListDiv.className = "tabList";
    document.getElementById('topDiv').appendChild(tabListDiv);
    Object.entries(tabs).forEach(([name, link]) => {
        const tabDiv = document.createElement("div");
        tabDiv.className = "tab";
        tabDiv.setAttribute("link", link);
        tabDiv.innerHTML = `<h2>${name}</h2>`;

        tabDiv.addEventListener("click", () => {
            window.location.href = link;
        });
        document.getElementById('tabList').appendChild(tabDiv);
    });
    $('.tab[link="'+window.location.href+'"]').addClass('active');
}
function removeHighlights() {
    $("mark").each(function() {
        // Replace the <mark> tag with its inner text
        $(this).replaceWith($(this).text());
    });
}
function highlightOccurrences(searchString) {
    // Loop through all elements on the page
    removeHighlights();    
    const regex = new RegExp(searchString, "gi");
    console.log(searchString, regex);
    $("body *").contents().each(function() {
        if (this.nodeType === 3) { // Only process text nodes
            const text = $(this).text();
                // Case-insensitive search
            // Replace occurrences with <mark>
            const highlightedText = text.replace(regex, function(match) {
                console.log('highlighting', match);
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