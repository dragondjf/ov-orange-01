pref("toolkit.defaultChromeURI", "chrome://ifpms/content/loginwin.xul");
pref("nglayout.debug.disable_xul_cache", true);
//pref("layout.fullScreen", true);

pref("toolkit.defaultChromeFeatures", "chrome,resizable=no");

//Single Instance
pref("toolkit.singletonWindowType", "IFPMS");

/* debugging prefs */
pref("browser.dom.window.dump.enabled", true);
pref("javascript.options.showInConsole", true);
pref("javascript.options.strict", true);
pref("nglayout.debug.disable_xul_cache", true);
pref("nglayout.debug.disable_xul_fastload", true);

/* Don't inherit OS locale */
pref("intl.locale.matchOS", "false");
/* Choose own fallback locale; later it can be overridden by the user */
pref("general.useragent.locale", "zh-CN");