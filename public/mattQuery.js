function addZero(n) {return (n < 10)? '00' + n : (n < 100)? '0' + n : '' + n;}
const tabs = {
    'XML Liste': "https://ig-creator.xxxlgroup.com/idm/XMLLister/xmlListerIndex.html",
    'XML Liste + Country': "https://ig-creator.xxxlgroup.com/idm/XMLLister/xmlListerCountryIndex.html",
    'XML Checker': "https://ig-creator.xxxlgroup.com/idm/XMLLister/xmlChecker_v3.html",
    'Registry Liste': "https://ig-creator.xxxlgroup.com/idm/XMLLister/xmlRegistryLister.html",
    '3D Modell&uuml;bersicht': "https://walm-dc.github.io/WebTools/public/3DModelOverview.html",
    '3D Modell-Details': "https://walm-dc.github.io/WebTools/public/3DModelDetails.html"
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