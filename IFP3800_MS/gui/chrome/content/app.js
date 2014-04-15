
(function() {

    // add window Event
    window.addEventListener("load", function() {
        Ifpms.initialize();
        Ifpms.Xpcom.startup();
        Ifpms.PaMgr.load();
        //mgmt.ini();
        alarmmgmt.tablemanager.showNewestAlarm();

    }, false);
    window.addEventListener("unload", function() {
        Ifpms.shutdown();
    }, false);

})();