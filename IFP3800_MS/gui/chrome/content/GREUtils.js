/*
 * GREUtils - is simple and easy use APIs libraries for GRE (Gecko Runtime Environment).
 *
 * Copyright (c) 2007 Rack Lin (racklin@gmail.com)
 *
 * $Date: 2008-08-18 10:25:28 +0800 (星期一, 18 八月 2008) $
 * $Rev: 9 $
 */
/**
 * GREUtils - is simple and easy use APIs libraries for GRE (Gecko Runtime Environment).
 * 
 * @public
 * @name GREUtils
 * @namespace GREUtils
 */
var GREUtils = GREUtils  ||  {version: "1.1"};

GREUtils.context = this;

GREUtils.global = (typeof window != 'undefined') ? window : this;


/**
 * Object Extend function
 * Extend one object with one or more others, returning the original, modified, object.
 *
 * @public
 * @static
 * @function
 * @param {Object} target
 * @param {Object} source
 * @param {Object} extras
 * @return {Object} target object
 */
GREUtils.extend = function () {
    // copy reference to target object
    var target = arguments[0] || {};
    var source = arguments[1] || {};
    var extras = arguments[2] || {};

    // Extend the base object
    for ( var i in source ) {
        // Prevent never-ending loop
        if ( target == source[i] )
            continue;

        // Don't bring in undefined values
        if ( source[i] != undefined )
            target[i] = source[i];
    }

    // Extend the extra object
    for ( var i in extras ) {
        // Prevent never-ending loop
        if ( target == extras[i] )
            continue;

        // Don't bring in undefined values
        if ( extras[i] != undefined )
            target[i] = extras[i];
    }

    // Return the modified object
    return target;
};


/**
 *  The intent of the Singleton pattern as defined in Design Patterns is to "ensure a class has only one instance, and provide a global point of access to it".
 *
 * @public
 * @static
 * @function
 * @param {Object | Function} target Object or Function constructor
 */
GREUtils.singleton = function(target) {
	
	GREUtils.extend(target, {
	    __instance__: null, //define the static property
	    
		// return single instance
	    getInstance: function getInstance(){
	    
	        if (this.__instance__ == null) {
	            this.__instance__ = new this();
	        }
	        
	        return this.__instance__;
	    }
	});
};



/**
 * Static variant of Function inherits.
 *
 * Use this._super to call parent method.
 * 
 * @public
 * @static
 * @function
 * @param {Function} childFunc Child class.
 * @param {Function} parentFunc Parent class.
 */
GREUtils.inherits = function(childFunc, parentFunc) {

	// The dummy class constructor
    function Class() {};
	
	// Populate our constructed prototype object
    Class.prototype = parentFunc.prototype;
	
	// Add a new ._super that is the super-class
    childFunc._super = parentFunc.prototype;
	
    childFunc.prototype = new Class();
	
	// Enforce the constructor to be what we expect
    childFunc.prototype.constructor = childFunc;
    
    // auto support singleton if parent getInstance exists
    if(typeof parentFunc.getInstance == 'function') {
        GREUtils.singleton(childFunc);
    }

};


/**
 * Define a namespace.
 *
 * @public
 * @static 
 * @function
 * @param name {String} namespace name
 * @param name {Object} context
 */
GREUtils.define = function(name, context) {

  GREUtils.createNamespace(name, {}, context);

};

/**
 * Builds an object structure for the provided namespace path,
 * example:
 * "a.b.c" -> a = {};a.b={};a.b.c={};
 * Used by GREUtils.namespace
 * 
 * @private
 * @function
 * @static
 * @param {string} name name of the object that this file defines.
 * @param {Object} object the object to expose at the end of the path.
 * @param {Object} context
 */
GREUtils.createNamespace = function(name, object, context) {
  var parts = name.split('.');
  var cur = context || GREUtils.global;
  var part;

  while ((part = parts.shift())) {
    if (!parts.length && GREUtils.isDefined(object)) {
      // last part and we have an object; use it
      cur[part] = object;
    } else if (cur[part]) {
      cur = cur[part];
    } else {
      cur = cur[part] = {};
    }
  }
};

/**
 * Check that the type is not undefined (we do it here as on
 * 
 * @public
 * @static
 * @function
 * @param {any} type
 * @return {Boolean}
 */
GREUtils.isDefined = function(type) {
    return typeof type != 'undefined';
};

/**
 * Returns true if val is a function.
 *
 * @public
 * @static
 * @function
 * @param {any} type
 * @return {Boolean}
 */
GREUtils.isFunction = function(type) {
  return typeof type == "function";
};

/**
 * Returns true if the specified value is |null|
 *
 * @public
 * @static
 * @function
 * @param {any} type
 * @return {Boolean}
 */
GREUtils.isNull = function(type) {
  return type === null;
};

/**
 * Returns true if the specified value is defined and not null
 *
 * @public
 * @static
 * @function
 * @param {any} type
 * @return {Boolean}
 */
GREUtils.isDefineAndNotNull = function(type) {
  return GREUtils.isDefined(type) && !GREUtils.isNull(type);
};

/**
 * Returns true if the specified value is an array
 *
 * @public
 * @static
 * @function
 * @param {any} type
 * @return {Boolean} variable is an array.
 */
GREUtils.isArray = function(type) {
  return typeof type == 'array';
};

/**
 * Returns true if the specified value is a string
 * 
 * @public
 * @static
 * @function
 * @param {any} type
 * @return {Boolean} Whether variable is a string.
 */
GREUtils.isString = function(type) {
  return typeof type == 'string';
};


/**
 * Returns true if the specified value is a boolean
 *
 * @public
 * @static
 * @function
 * @param {any} type 
 * @return {Boolean} Whether variable is boolean.
 */
GREUtils.isBoolean = function(type) {
  return typeof type == 'boolean';
};


/**
 * Returns true if the specified value is a number
 *
 * @public
 * @static
 * @function
 * @param {any} type
 * @return {Boolean} Whether variable is a number.
 */
GREUtils.isNumber = function(type) {
  return typeof type == 'number';
};

/**
 * Returns true if the specified value is an object.  This includes arrays
 * and functions.
 *
 * @public
 * @static
 * @function
 * @param {any} type 
 * @return {Boolean} Whether variable is an object.
 */
GREUtils.isObject = function(type) {
  var type = typeof type;
  return type == 'object' || type == 'array' || type == 'function';
};

/**
 * new Date().getTime().
 *
 * @public
 * @static
 * @function
 * @param {any} type
 * @return {Number} An integer value representing the number of milliseconds
 *     between midnight, January 1, 1970 and the current time.
 */
GREUtils.now = Date.now || (function() {
  return new Date().getTime();
});
/**
 * XPCOM Utilities
 * 
 * @public 
 * @name GREUtils.XPCOM
 * @namespace GREUtils.XPCOM 
 */
GREUtils.define('GREUtils.XPCOM');

try {
    // try assign Components.classes for privilege check // shortcut by exception :D
    var _CC = Components.classes;
    GREUtils.XPCOM._EnablePrivilege = true;
}catch(ex) {
    // need Privilege and any XPCOM Operation need enablePrivilege.
    // netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect");
    GREUtils.XPCOM._EnablePrivilege = false;
}

/**
 * Return class from Components.classes by ClassName.
 *
 * return null if ClassName not exists.
 *
 * @public
 * @static
 * @function 
 * @param {String} className
 * @return {Object}
 */
GREUtils.XPCOM.Cc = function (cName) {
    try {
        if(cName in Components.classes) return Components.classes[cName];
        return null;
    }catch(ex) {
        // netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect");
		GREUtils.log('[Error] GREUtils.XPCOM.Cc: '+ex.message);
        return null;
    }
};


/**
 * Return interface from Components.interfaces by Interface Name.
 *
 * return null if Interface Name not exists.
 *
 * @public
 * @static
 * @function 
 * @param {String} interfaceName
 * @return {Object}
 */
GREUtils.XPCOM.Ci = function (ifaceName) {
    try {
        switch (typeof(ifaceName)) {
            case "object":
                return ifaceName; 
                break;

            case "string":
                return Components.interfaces[ifaceName];
                break;       
        }
    } catch (ex) {
		GREUtils.log('[Error] GREUtils.XPCOM.Ci: '+ex.message);
        return null;
    }
};


/**
 * Return Components.results or [].
 *
 * @public
 * @static
 * @function 
 * @return {Array}
 */
GREUtils.XPCOM.Cr = function (){
    try {
        return Components.results;
    }catch(ex) {
        GREUtils.log('[Error] GREUtils.XPCOM.Cr: '+ex.message);
        return [];
    }
};


/**
 * Return Class Instance by getService.
 *
 * return null if ClassName or Interface not exists.
 *
 * @public
 * @static
 * @function 
 * @param {String} className
 * @param {String} interfaceName
 * @return {Object}
 */
GREUtils.XPCOM.getService = function (cName, ifaceName) {
    var cls = GREUtils.XPCOM.Cc(cName);
    var iface = GREUtils.XPCOM.Ci(ifaceName);
    
    try {
        if (cls && iface) {
            return cls.getService(iface);
        }
        else if (cls) {
                return cls.getService();
        }
        return null;
    } 
    catch (ex) {
		GREUtils.log('[Error] GREUtils.XPCOM.getService: '+ex.message);
        return null;
    }
};


/**
 * Return Class Instance by createInstance.
 *
 * return null if ClassName or Interface not exists.
 *
 * @public
 * @static
 * @function 
 * @param {String} className
 * @param {String} interfaceName
 * @return {Object}
 */
GREUtils.XPCOM.createInstance = function (cName, ifaceName) {
    var cls = GREUtils.XPCOM.Cc(cName);
    var iface = GREUtils.XPCOM.Ci(ifaceName);

    try {
        if (cls && iface) {
            return cls.createInstance(iface);
        }
    } 
    catch (ex) {
		GREUtils.log('[Error] GREUtils.XPCOM.createInstance: '+ex.message);
        return null;
    }
};


/**
 * Query Class Interface.
 *
 * @public
 * @static
 * @function 
 * @param {String} className
 * @param {String} interfaceName
 * @return {Object}
 */
GREUtils.XPCOM.queryInterface = function (obj, ifaceName) {

    if (typeof(obj) == "object") {
        var iface = GREUtils.XPCOM.Ci(ifaceName);
		try {
		  if (iface) return obj.QueryInterface(iface);	
		}catch(ex) {
			GREUtils.log('[Error] GREUtils.XPCOM.queryInterface: '+ex.message);
		  return null;
		}
    }
    return obj;

};


/**
 * Get Class Constructor.
 *
 * @public
 * @static
 * @function 
 * @param {String} className
 * @param {String} interfaceName
 * @return {Object}
 */
GREUtils.XPCOM.getConstructor = function (aCID, aInterface, aFunc) {
  try {
    if (aFunc) {
		return new Components.Constructor(aCID, aInterface, aFunc);
	}
	else {
		return new Components.Constructor(aCID, aInterface);
	}
  } catch (ex) { 
      GREUtils.log('[Error] GREUtils.XPCOM.getConstructor: ' + ex.message);
  	return null; 
  }
};

/**
 * Predefine useful XPCOM Service Name and Interface
 *
 * @private
 * @static
 * @field  
 */
GREUtils.XPCOM._usefulServiceMap = {
    "jssubscript-loader": ["@mozilla.org/moz/jssubscript-loader;1", "mozIJSSubScriptLoader"],
    "app-info": ["@mozilla.org/xre/app-info;1", "nsIXULAppInfo"],
    "runtime-info": ["@mozilla.org/xre/app-info;1", "nsIXULRuntime"],
    "app-startup": ['@mozilla.org/toolkit/app-startup;1','nsIAppStartup'],
	"sound": ["@mozilla.org/sound;1", "nsISound"],
    "observer-service": ["@mozilla.org/observer-service;1", "nsIObserverService"],
    "consoleservice": ["@mozilla.org/consoleservice;1", "nsIConsoleService"],
	"prompt-service": ["@mozilla.org/embedcomp/prompt-service;1", "nsIPromptService"],
	"window-mediator": ["@mozilla.org/appshell/window-mediator;1","nsIWindowMediator"],
	"window-watcher": ["@mozilla.org/embedcomp/window-watcher;1","nsIWindowWatcher"],
	"thread-manager": ["@mozilla.org/thread-manager;1", "nsIThreadManager"],
	"idleservice": ["@mozilla.org/widget/idleservice;1", "nsIIdleService"],
	"json": ["@mozilla.org/dom/json;1", "nsIJSON"],
	"unicodeconverter": ["@mozilla.org/intl/scriptableunicodeconverter","nsIScriptableUnicodeConverter"],
	"hash": ["@mozilla.org/security/hash;1", "nsICryptoHash"],
	"xmlhttprequest": ["@mozilla.org/xmlextras/xmlhttprequest;1", "nsIXMLHttpRequest"]
};


/**
 * Predefine useful XPCOM Service object pool.
 *
 * @private
 * @static
 * @field  
 */
GREUtils.XPCOM._usefulServicePool = {};


/**
 * Get Useful Services.
 *
 * @public
 * @static 
 * @function
 * @param {String} serviceName
 * @return {Object}
 */
GREUtils.XPCOM.getUsefulService = function (serviceName) {
	if (GREUtils.XPCOM._usefulServicePool[serviceName] && GREUtils.isXPCOM(GREUtils.XPCOM._usefulServicePool[serviceName]))
		return GREUtils.XPCOM._usefulServicePool[serviceName];

	if(serviceName in GREUtils.XPCOM._usefulServiceMap) {
		var service = this.getService(GREUtils.XPCOM._usefulServiceMap[serviceName][0], GREUtils.XPCOM._usefulServiceMap[serviceName][1]);
		if (GREUtils.isXPCOM(service)) {
			GREUtils.XPCOM._usefulServicePool[serviceName] = service;
			return GREUtils.XPCOM._usefulServicePool[serviceName];	
		} else {
			return null;
		}
         
    }
    return null; 
};


/**
 * Returns true if val is a xpcom components.
 *
 * XPCom components must implement nsISupports Interface.
 * 
 * @public
 * @static 
 * @function
 * @param {Object} val
 * @return {Boolean}
 */
GREUtils.isXPCOM = function(val) {
	var res = GREUtils.XPCOM.queryInterface(val, "nsISupports");
    return res != null && typeof res == "object";
};
/*
 * Useful Functions
 */
GREUtils._data = {};


/**
 * Get Application Infomation.
 *
 * see nsIXULAppInfo Interface.
 *
 * @public
 * @static
 * @function 
 * @return {Object}
 */
GREUtils.getAppInfo = function () {
    return GREUtils.XPCOM.getUsefulService("app-info");
};


/**
 * Get Runtime Infomation.
 *
 * see nsIXULRuntime Interface.
 *
 * @public
 * @static
 * @function 
 * @return {Object}
 */
GREUtils.getRuntimeInfo = function() {
    return GREUtils.XPCOM.getUsefulService("runtime-info");
};


/**
 * Get OS Infomation.
 *
 * see nsIXULRuntime Interface.
 *
 * @public
 * @static
 * @function 
 * @return {Object}
 */
GREUtils.getOSInfo = function() {
    return GREUtils.getRuntimeInfo().OS;
    
};

 
/**
 * is Linux OS
 *
 * @public
 * @static
 * @function 
 * @return {Boolean}
 */
GREUtils.isLinux = function(){
    return (GREUtils.getOSInfo().match(/Linux/,"i").length > 0);
};


/**
 * is Window OS
 *
 * @public
 * @static
 * @function 
 * @return {Boolean}
 */
GREUtils.isWindow = function() {
    return (GREUtils.getOSInfo().match(/Win/,"i").length > 0);
};


/**
 * is Mac OS
 *
 * @public
 * @static
 * @function 
 * @return {Boolean}
 */
GREUtils.isMac =function() {
    return (GREUtils.getOSInfo().match(/Mac|Darwin/,"i").length > 0);
};


/**
 * Synchronously loads and executes the script from the specified URL.
 *
 * default scope is window.
 *
 * @public
 * @static
 * @function 
 * @param {Object} scriptSrc
 * @param {Object} scope
 */
GREUtils.include = function (scriptSrc, scope) {

    var objScope = scope || GREUtils.global;

    if (scriptSrc.indexOf('://') == -1) {
        scriptSrc = document.location.href.substring(0, document.location.href.lastIndexOf('/') +1) + scriptSrc;
    }

    var rv;
    try {
        if(!GREUtils.XPCOM._EnablePrivilege) netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect");
        GREUtils.XPCOM.getUsefulService("jssubscript-loader").loadSubScript(scriptSrc, objScope);
        rv = GREUtils.XPCOM.Cr().NS_OK;
    } catch (e) {
		GREUtils.log('[Error] GREUtils.include: '+e.message + "("+scriptSrc+")");
        rv = - GREUtils.XPCOM.Cr().NS_ERROR_INVALID_ARG;
    }
    return rv;
};


/**
 * Synchronously loads and executes the script from the specified URL.
 *
 * Specified URL will loads and executes once.
 *
 * default scope is window.
 *
 * @public
 * @static
 * @function 
 * @param {Object} scriptSrc
 * @param {Object} scope
 */
GREUtils.include_once = function(scriptSrc, scope) {

    var scriptJS = scriptSrc.substring( scriptSrc.lastIndexOf('/') + 1, scriptSrc.length );
    var scriptJS_loaded = encodeURIComponent(scriptJS)+"_LOADED";
    if(scriptJS_loaded in this._data) {
        return GREUtils.XPCOM.Cr().NS_OK;
    } else {
		var rv ;
        rv = this.include(scriptSrc, scope);
        if(rv == GREUtils.XPCOM.Cr().NS_OK) {
            this._data[scriptJS_loaded] = rv;
        }
        return rv;
    }
};


/**
 * This method was introduced in Firefox 3.
 * Is used for sharing code between different scopes easily.
 *
 * @public
 * @static
 * @function 
 * @name GREUtils.import
 * @param {Object} url
 * @param {Object} scope
 */
GREUtils.import_ = function(url, scope) {

	if(arguments.length == 1) {
		Components.utils['import']( url );		
	}else if(arguments.length == 2) {
		Components.utils['import']( url, scope );
	}
};

GREUtils['import'] = GREUtils.import_;

/**
 * Convert XUL String to DOM Elements.
 *
 * XUL String namespace is http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul
 * You can specified your custom namespace.
 *
 * @public
 * @static
 * @function 
 * @param {String} xulString
 * @param {String} xmlns
 * @return {Object}
 */
GREUtils.domXULString = function (xulString, xmlns) {

    var xmlns = xmlns || "http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul";
	
    // try with box container and namespace for easy use.
    var xulString2 = '<box xmlns="'+xmlns+'">'+xulString+'</box>';

    var parser=new DOMParser();
    var resultDoc=parser.parseFromString(xulString2,"text/xml");

    if (resultDoc.documentElement.tagName == "parsererror") {
        return null;
    } else {
        if (resultDoc.documentElement.childNodes.length == 1) {
            return resultDoc.documentElement.firstChild;
        }
        else {
            return resultDoc.documentElement;
        }
    }
};


/**
 * Convert HTML String to DOM Elements.
 *
 * HTML String namespace is http://www.w3.org/1999/xhtml
 * You can specified your custom namespace.
 *
 * @public
 * @static
 * @function 
 * @param {String} htmlString
 * @param {String} xmlns
 * @return {Object}
 */
GREUtils.domHTMLString = function (htmlString, xmlns) {

    var xmlns = xmlns || "http://www.w3.org/1999/xhtml";
	
    // try with div container and namespace for easy use.
    var htmlString2 = '<div xmlns="'+xmlns+'">'+htmlString+'</div>';

    var parser=new DOMParser();
    var resultDoc=parser.parseFromString(htmlString2,"text/xml");
	
    if (resultDoc.documentElement.tagName == "parsererror") {
		return null;
	} else {
		if (resultDoc.documentElement.childNodes.length == 1) 
			return resultDoc.documentElement.firstChild;
		else 
			return resultDoc.documentElement;
	}

};


/**
 * Quit Application
 *
 * see nsIAppStartup
 *
 * @public
 * @static
 * @function 
 * @param {Number} mode
 */
GREUtils.quitApplication = function() {
    var mode = arguments[0] || Components.interfaces.nsIAppStartup.eAttemptQuit;
    GREUtils.XPCOM.getUsefulService("app-startup").quit(mode);
};


/**
 * Restart Application
 *
 * see nsIAppStartup
 *
 * @public
 * @static
 * @function 
 */
GREUtils.restartApplication = function() {
    GREUtils.quitApplication((Components.interfaces.nsIAppStartup.eRestart | Components.interfaces.nsIAppStartup.eAttemptQuit));
};


/**
 * Ram Back  notifyObservers memory-pressure
 *
 * see memory-pressure
 *
 * @public
 * @static
 * @function 
 */
GREUtils.ramback = function() {
    var observerService = GREUtils.XPCOM.getUsefulService("observer-service"); 
    
    // since we don't know the order of how things are going to go, fire these multiple times
    observerService.notifyObservers(null, "memory-pressure", "heap-minimize");
    observerService.notifyObservers(null, "memory-pressure", "heap-minimize");
    observerService.notifyObservers(null, "memory-pressure", "heap-minimize");

};

    
/**
 * Use Console.logStringMessage(msg);
 *
 * @public
 * @static
 * @function
 * @param {String} log message 
 */
GREUtils.log = function (sMsg) {
    GREUtils.XPCOM.getUsefulService("consoleservice").logStringMessage(sMsg);
};


/**
 * UUID Generator -  use XPCOM base for fast uuid generate.
 * 
 * @public
 * @static
 * @function
 * @return {String} uuid string 
 */
GREUtils.uuid  = function () {
	var uuid = GREUtils.XPCOM.getService("@mozilla.org/uuid-generator;1","nsIUUIDGenerator").generateUUID().number;
	uuid = uuid.replace(/^{|}$/g, '');	    
    return uuid;
};


/**
 * Get Idle Time - 
 * The amount of time in milliseconds that has passed since the last user activity.
 * Firefox3 and XULrunner 1.9 above only.
 * 
 * @public
 * @static
 * @function 
 * @return {Number} idle time
 */
GREUtils.getIdleTime = function() {
    return GREUtils.XPCOM.getUsefulService("idleservice").idleTime;
};


/**
 * getIdleObserver Helper
 * 
 * call register for Register IdleObserver 
 * call unregister for Remove IdleObserver
 * 
 * Firefox3 and XULrunner 1.9 above only.
 * 
 * @public
 * @static
 * @function 
 * @param {Function} func
 * @param {Integer} time
 * @return {Object} idle Observer Object
 */
GREUtils.getIdleObserver = function(func, time) {
	
	var idleObserver = {
		time: time,
		
        observe: function(subject, topic, data){
			try {
			 func(subject, topic, data);
			}catch(e) {
				
			}
		},
		
		unregister: function() {
			GREUtils.XPCOM.getUsefulService("idleservice").removeIdleObserver(this, this.time);
		},
		
		register: function() {
			GREUtils.XPCOM.getUsefulService("idleservice").addIdleObserver(this, this.time);
		}
    };

    return idleObserver;
};


/**
 * base-64 encode of a string
 * 
 * @public
 * @static
 * @function 
 * @param {String} str
 * @return {String} base64 string
 */
GREUtils.base64Encode = function(){
	window.atob.apply(GREUtils.global, arguments);
};

/**
 * base-64 decode of a string
 * 
 * @public
 * @static
 * @function 
 * @param {String} str
 * @return {String}
 */
GREUtils.base64Decode = function(){
	window.btoa.apply(GREUtils.global, arguments);
};

/** 
 * Uppercase the first character of each word in a string
 *
 * @public
 * @static
 * @function 
 * @param {String} word
 * @return {String}
 */
GREUtils.ucwords = function(word) {
    return word.replace(/^(.)|\s(.)/g, function ( $1 ) { return $1.toUpperCase ( ); } );
};


/**
 * Make a string's first character uppercase
 *
 * @public
 * @static
 * @function 
 * @param {String} word
 * @return {String}
 */
GREUtils.ucfirst = function(word) {
    var f = word.charAt(0).toUpperCase();
    return f + word.substr(1, word.length-1);
};
/**
 *  XPCOM File System Services
 *
 * @public
 * @name GREUtils.File
 * @namespace GREUtils.File
 */
GREUtils.define('GREUtils.File');

GREUtils.File = {
	
	FILE_RDONLY:       0x01,
	FILE_WRONLY:       0x02,
	FILE_RDWR:         0x04,
	FILE_CREATE_FILE:  0x08,
	FILE_APPEND:       0x10,
	FILE_TRUNCATE:     0x20,
	FILE_SYNC:         0x40,
	FILE_EXCL:         0x80,
    
    FILE_READ_MODE: "r",
    FILE_WRITE_MODE: "w",
    FILE_APPEND_MODE: "a",
    FILE_BINARY_MODE: "b",
    
    NORMAL_FILE_TYPE: 0x00,
	DIRECTORY_TYPE:   0x01,

    FILE_CHUNK: 1024, // buffer for readline => set to 1k
    FILE_DEFAULT_PERMS: 0644,
	DIR_DEFAULT_PERMS:  0755
};


/**
 * Get File or Path ILocalFile Interface
 *
 * @public
 * @static
 * @function
 * @param {String} sFile
 * @return {Object}
 */
GREUtils.File.getFile = function(sFile){
    var autoCreate = arguments[1] || false;
    if (/^file:/.test(sFile))
	if (GREUtils.isWindow())
	    sFile = sFile.replace("file:///","","gm").replace("/","\\","gm");
	else 
	    sFile = sFile.replace("file://", "");
    var obj = GREUtils.XPCOM.createInstance('@mozilla.org/file/local;1', 'nsILocalFile');
    obj.initWithPath(sFile);
    if (obj.exists()) 
        return obj;
    else 
        if (autoCreate) {
            try {
                obj.create(GREUtils.File.NORMAL_FILE_TYPE, GREUtils.File.FILE_DEFAULT_PERMS);
                return obj;
            } 
            catch (ex) {
                return null;
            }
        }
        else {
            return null;
        }
};


/**
 * Get URL nsIURL Interface.
 *
 * @public
 * @static
 * @function
 * @param {Object} sURL
 */
GREUtils.File.getURL = function(sURL){
    var mURL = null;
    if (!/^file:/.test(sURL)) {
        mURL = GREUtils.XPCOM.createInstance("@mozilla.org/network/standard-url;1", "nsIURL");
        mURL.spec = sURL;
    }
    else {
        mURL = GREUtils.XPCOM.getService("@mozilla.org/network/io-service;1", "nsIIOService").newURI(sURL, "UTF-8", null);
        mURL = GREUtils.XPCOM.queryInterface(mURL, "nsIFileURL");
    }
    return mURL;
};


/**
 * Get File OutputStream
 *
 * @public
 * @static
 * @function
 * @param {Object} file
 * @param {String} mode
 * @param {Number} perm
 */
GREUtils.File.getOutputStream = function(file, mode, perm){
    var nsIFile = (typeof(file) == "string") ? this.getFile(file) : file;
    
    var NS_MODE = (GREUtils.File.FILE_TRUNCATE | GREUtils.File.FILE_WRONLY);
    if (typeof(mode) == "string" && mode.indexOf("w") != -1) 
        NS_MODE = (GREUtils.File.FILE_TRUNCATE | GREUtils.File.FILE_WRONLY);
    if (typeof(mode) == "string" && mode.indexOf("a") != -1) 
        NS_MODE = (GREUtils.File.FILE_APPEND | GREUtils.File.FILE_RDWR);
    
    var nsPerm = perm || GREUtils.File.FILE_DEFAULT_PERMS;
    
    if (nsIFile == null) {
        var nsIFile = GREUtils.XPCOM.createInstance('@mozilla.org/file/local;1', 'nsILocalFile');
        nsIFile.initWithPath(file);
        nsIFile.create(GREUtils.File.NORMAL_FILE_TYPE, nsPerm);
    }
    
    var fs = GREUtils.XPCOM.createInstance("@mozilla.org/network/file-output-stream;1", "nsIFileOutputStream");
    
    fs.init(nsIFile, NS_MODE, nsPerm, null);
    
    if (typeof(mode) == "string" && mode.indexOf("b") != -1) {
        var binstream = GREUtils.XPCOM.createInstance("@mozilla.org/binaryoutputstream;1", "nsIBinaryOutputStream");
        binstream.setOutputStream(fs);
        return binstream;
    }
    else 
        return fs;
    
};

/**
 * Get File InputStream
 *
 * @public
 * @static
 * @function
 * @param {Object} file
 * @param {String} mode
 * @param {Number} perm
 */
GREUtils.File.getInputStream = function(file, mode, perm){
    var nsIFile = (typeof(file) == "string") ? this.getFile(file) : file;
    
    if (nsIFile == null) 
        return null;
    
    var NS_MODE = GREUtils.File.FILE_RDONLY;
    if (typeof(mode) == "string" && mode.indexOf("r") != -1) 
        NS_MODE = GREUtils.File.FILE_RDONLY;
    
    var nsPerm = perm || GREUtils.File.FILE_DEFAULT_PERMS;
    
    var fs = GREUtils.XPCOM.createInstance("@mozilla.org/network/file-input-stream;1", "nsIFileInputStream");
    
    fs.init(nsIFile, NS_MODE, nsPerm, null);
    
    if (typeof(mode) == "string" && mode.indexOf("b") != -1) {
        var binstream = GREUtils.XPCOM.createInstance("@mozilla.org/binaryinputstream;1", "nsIBinaryInputStream");
        binstream.setInputStream(fs);
        return binstream;
    }
    else {
        var scriptstream = GREUtils.XPCOM.createInstance("@mozilla.org/scriptableinputstream;1", "nsIScriptableInputStream");
        scriptstream.init(fs);
        return scriptstream;
    }
};

/**
 * Get File LineInputStream
 *
 * see nsILineInputStream
 *
 * @public
 * @static
 * @function
 * @param {Object} file
 * @return {Object}
 */
GREUtils.File.getLineInputStream = function(file){
    var nsIFile = (typeof(file) == "string") ? this.getFile(file) : file;
    if (nsIFile == null) 
        return null;
    
    var fs = GREUtils.XPCOM.createInstance("@mozilla.org/network/file-input-stream;1", "nsIFileInputStream");
    fs.init(nsIFile, GREUtils.File.FILE_RDONLY, GREUtils.File.FILE_DEFAULT_PERMS, null);
    return GREUtils.XPCOM.queryInterface(fs, "nsILineInputStream");
};

/**
 * Read File Contents to Array
 *
 * @public
 * @static
 * @function
 * @param {Object} file
 * @return {Array}
 */
GREUtils.File.readAllLine = function(file){
    var lineStream = this.getLineInputStream(file);
    var lines = [];
    var buf = {
        value: ""
    };
    
    if (!lineStream) 
        return lines;
    
    do {
        var rv = lineStream.readLine(buf);
        lines.push(buf.value);
    }
    while (rv);
    
    lineStream.close();
    return lines;
};

/**
 * Read File Contents to Binary String.
 *
 * @public
 * @static
 * @function
 * @param {Object} file
 * @return {String}
 */
GREUtils.File.readAllBytes = function(file){
    var nsIFile = (typeof(file) == "string") ? this.getFile(file) : file;
    var size = nsIFile.fileSize;
    var binStream = this.getInputStream(nsIFile, "rb", GREUtils.File.FILE_DEFAULT_PERMS);
    var binaryString = binStream.readBytes(size);
    binStream.close();
    return binaryString;
    
};


/**
 * Write Array Contents to File
 *
 * @public
 * @static
 * @function
 * @param {Object} file
 * @param {Array} lines
 */
GREUtils.File.writeAllLine = function(file, lines){
    var outputStream = this.getOutputStream(file, "w");
    
    if (!outputStream) 
        return;
    
    lines.forEach(function(buf){
        buf = "" + buf;
        outputStream.write(buf + "\n", buf.length + 1);
    });
    
    outputStream.close();
};

/**
 * Write Binary String Contents to File
 *
 * @public
 * @static
 * @function
 * @param {Object} file
 * @param {String} buf
 */
GREUtils.File.writeAllBytes = function(file, buf){
    var outputStream = this.getOutputStream(file, "wb");
    
    if (!outputStream) 
        return;
    
    outputStream.write(buf, buf.length);
    
    outputStream.close();
};


/**
 * Executes the file
 *
 * blocking: Whether to wait until the process terminates before returning or not
 *
 * @public
 * @static
 * @function
 * @param {Object} nsFile
 * @param {Object} aArgs
 * @param {Boolean} blocking
 * @return {Number}
 */
GREUtils.File.run = function(nsFile, aArgs, blocking){
    var nsIFile = (typeof(nsFile) == "string") ? this.getFile(nsFile) : nsFile;
    if (nsIFile == null) 
        return -1;
    if (nsIFile.isDirectory()) 
        return -2;
    
    var blocking = blocking || false;
    
    try {
        var process = GREUtils.XPCOM.createInstance("@mozilla.org/process/util;1", "nsIProcess");
        // var process = GREUtils.XPCOM.getService("@mozilla.org/process/util;1", "nsIProcess");
        
        process.init(nsIFile);
        
        var len = 0;
        if (aArgs) 
            len = aArgs.length;
        else 
            aArgs = null;
        rv = process.run(blocking, aArgs, len);
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.run: '+e.message);
        rv = -3
    }
    return rv;
};

/**
 * Executes the file
 *
 * blocking: Whether to wait until the process terminates before returning or not
 *
 * @public
 * @static
 * @function
 * @param {Object} nsFile
 * @param {Object} aArgs
 * @return {Number}
 */
GREUtils.File.exec = function(){
    GREUtils.File.run.apply(this, arguments);
}

/**
 * Convert chrome:// URL to URL spec.
 *
 * @public
 * @static
 * @function
 * @param {String} chromePath
 * @return {String} url
 */
GREUtils.File.chromeToURL = function(chromePath){
    var uri = this.getURL(chromePath);
    var cr = GREUtils.XPCOM.getService("@mozilla.org/chrome/chrome-registry;1", "nsIChromeRegistry");
    var rv = null;
    try {
        var result = cr.convertChromeURL(uri);
        if (!GREUtils.isString(result)) {
            rv = cr.convertChromeURL(uri).spec;
        }
        else {
            rv = result;
        }
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.chromeToURL: '+e.message);
        rv = null;
    }
    return rv;
};

/**
 * Convert chrome:// URL to file path
 *
 * @public
 * @static
 * @function
 * @param {String} chromePath
 * @return {String} filepath
 */
GREUtils.File.chromeToPath = function(chromePath){
    var uri = this.getURL(chromePath);
    var cr = GREUtils.XPCOM.getService("@mozilla.org/chrome/chrome-registry;1", "nsIChromeRegistry");
    var rv = null;
    try {
        var result = cr.convertChromeURL(uri);
        if (!GREUtils.isString(result)) {
            result = cr.convertChromeURL(uri).spec;
        }
        
        if (!/^file:/.test(result)) 
            result = "file://" + result;
        
        var fph = GREUtils.XPCOM.getService("@mozilla.org/network/protocol;1?name=file", "nsIFileProtocolHandler");
        rv = fph.getFileFromURLSpec(result).path;
        
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.chromeToPath: '+e.message);
        rv = null;
    }
    return rv;
};


/**
 * Check if file exists
 *
 * @param {Object} aFile
 * @return {Boolean}
 */
GREUtils.File.exists = function(aFile){

    if (!aFile) 
        return false;
    
    var rv;
    try {
        rv = GREUtils.File.getFile(aFile).exists();
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.exists: '+e.message);
        rv = false;
    }
    
    return rv;
};

/**
 * REMOVE file  if file exists
 *
 * @param {Object} aFile
 * @return {Boolean}
 */
GREUtils.File.remove = function(aFile){

    if (!aFile) 
        return false;
    
    var rv;
    var file;
    try {
        file = GREUtils.File.getFile(aFile);
        
        if (file.isDirectory()) 
            return false;
        
        file.remove(false);
        return true;
        
        
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.remove: '+e.message);
        rv = false;
    }
    
    return rv;
};

/**
 * copy file
 * @param {String} aSource
 * @param {String} aDest
 * @return {Boolean} if success
 */
GREUtils.File.copy = function(aSource, aDest){

    if (!aSource || !aDest) 
        return false;
    
    if (!GREUtils.File.exists(aSource)) 
        return false;
    
    var rv;
    try {
        var fileInst = GREUtils.File.getFile(aSource);
        var dir = GREUtils.File.getFile(aDest);
        var copyName = fileInst.leafName;
        
        if (fileInst.isDirectory()) 
            return false;
        
        if (!GREUtils.File.exists(aDest) || !dir.isDirectory()) {
            copyName = dir.leafName;
            dir = GREUtils.File.getFile(dir.path.replace(copyName, ''));
            
            if (!GREUtils.File.exists(dir.path)) 
                return false;
            
            if (!dir.isDirectory()) 
                return false;
        }
        
        if (GREUtils.File.exists(GREUtils.File.append(dir.path, copyName))) 
            return false;
        
        fileInst.copyTo(dir, copyName);
        rv = true;
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.copy: '+e.message);
        return false;
    }
    
    return rv;
};

/**
 * append filename
 * 
 * @param {String} aDirPath
 * @param {String} aFileName
 * @return {String} filePath , empty String if error.
 */
GREUtils.File.append = function(aDirPath, aFileName){

    if (!aDirPath || !aFileName) 
        return "";
    
    if (!GREUtils.File.exists(aDirPath)) 
        return "";
    
    var rv;
    try {
        var fileInst = GREUtils.File.getFile(aDirPath);
        if (fileInst.exists() && !fileInst.isDirectory()) 
            return "";
        
        fileInst.append(aFileName);
        rv = fileInst.path;
        delete fileInst;
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.append: '+e.message);
        return "";
    }
    
    return rv;
};


/**
 * File Permissions 
 * 
 * @param {String} aPath
 * @return {Number} 
 */
GREUtils.File.permissions = function(aPath){

    if (!aPath) 
        return 0;
    
    if (!GREUtils.File.exists(aPath)) 
        return 0;
    
    var rv;
    try {
        rv = (GREUtils.File.getFile(aPath)).permissions.toString(8);
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.permissions: '+e.message);
        rv = 0;
    }
    
    return rv;
    
};

/**
 * File Date Modified.
 * 
 * @param {String} aPath
 * @return {Date}
 */
GREUtils.File.dateModified = function(aPath){
	
    if (!aPath) return null;
    
    if (!this.exists(aPath)) return null;
    
    var rv;
    try {
        rv = new Date((GREUtils.File.getFile(aPath)).lastModifiedTime).toLocaleString();
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.dateModified: '+e.message);
        rv = null;
    }
    
    return rv;
};

/**
 * SIZE
 * 
 * @param {String} aPath
 * @return {Number}  
 */
GREUtils.File.size = function(aPath){

    if (!aPath) 
        return -1;
    
    if (!GREUtils.File.exists(aPath)) 
        return -1;
    
    var rv = 0;
    try {
        rv = (GREUtils.File.getFile(aPath)).fileSize;
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.size: '+e.message);
        rv = -1;
    }
    
    return rv;
};

/**
 * EXTENSION
 * 
 * @param {String} aPath
 * @return {String} filePath , empty String if error.
 */
GREUtils.File.ext = function(aPath){

    if (!aPath) 
        return "";
    
    if (!GREUtils.File.exists(aPath)) 
        return "";
    
    var rv;
    try {
        var leafName = (GREUtils.File.getFile(aPath)).leafName;
        var dotIndex = leafName.lastIndexOf('.');
        rv = (dotIndex >= 0) ? leafName.substring(dotIndex + 1) : "";
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.ext: '+e.message);
        return ""
    }
    
    return rv;
};

/**
 * PARENT
 * 
 * @param {String} aPath
 * @return {String} filePath , empty String if error.
 */
GREUtils.File.parent = function(aPath){
    if (!aPath) 
        return "";
    
    var rv;
    try {
        var fileInst = GREUtils.File.getFile(aPath);
        
        if (!fileInst.exists()) 
            return "";
        
        if (fileInst.isFile()) 
            rv = fileInst.parent.path;
        
        else 
            if (fileInst.isDirectory()) 
                rv = fileInst.path;
            
            else 
                rv = "";
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.parent: '+e.message);
        rv = "";
    }
    
    return rv;
};


/**
 * isDir
 * 
 * @param {String} aPath 
 * @return {Boolean} 
 */
GREUtils.File.isDir = function(aPath){
	    
	var rv = false; 
    try {
		var fileInst = GREUtils.File.getFile(aPath);
		rv = fileInst.isDirectory();
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.isDir: '+e.message);
        rv = false;
    }
    return rv;
};

/**
 * isFile
 * 
 * @param {String} aPath  
 * @return {Boolean} 
 */
GREUtils.File.isFile = function(aPath){

	var rv = false; 
    try {
		var fileInst = GREUtils.File.getFile(aPath);
		rv = fileInst.isFile();
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.isFile: '+e.message);
        rv = false;
    }
    return rv;
};

/**
 * isExecutable
 * 
 * @param {String} aPath  
 * @return {Boolean} 
 */
GREUtils.File.isExecutable = function(aPath){

	var rv = false; 
    try {
		var fileInst = GREUtils.File.getFile(aPath);
		rv = fileInst.isExecutable();
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.isExecutable: '+e.message);
        rv = false;
    }
    return rv;
	
};


/**
 * isSymlink
 * 
 * @param {String} aPath  
 * @return {Boolean} 
 */
GREUtils.File.isSymlink = function(aPath){

	var rv = false; 
    try {
		var fileInst = GREUtils.File.getFile(aPath);
		rv = fileInst.isSymlink();
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.isSymlink: '+e.message);
        rv = false;
    }
    return rv;

};

/**
 * isWritable
 * 
 * @param {String} aPath  
 * @return {Boolean} 
 */
GREUtils.File.isWritable = function(aPath){

	var rv = false; 
    try {
		var fileInst = GREUtils.File.getFile(aPath);
		rv = fileInst.isWritable();
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.isWritable: '+e.message);
        rv = false;
    }
    return rv;
};

/**
 * isHidden
 * 
 * @param {String} aPath  
 * @return {Boolean} 
 */
GREUtils.File.isHidden = function(aPath){

	var rv = false; 
    try {
		var fileInst = GREUtils.File.getFile(aPath);
		rv = fileInst.isHidden();
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.isHidden: '+e.message);
        rv = false;
    }
    return rv;

};

/**
 * isSpecial
 * 
 * @param {String} aPath  
 * @return {Boolean} 
 */
GREUtils.File.isSpecial = function(aPath){

	var rv = false; 
    try {
		var fileInst = GREUtils.File.getFile(aPath);
		rv = fileInst.isSpecial();
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.isSpecial: '+e.message);
        rv = false;
    }
    return rv;

};

/**
 * normalize
 *
 * @param {String} aPath  
 * @return {Number}
 */
GREUtils.File.normalize = function(aPath){

	var rv; 
    try {
		var fileInst = GREUtils.File.getFile(aPath);
		rv = fileInst.normalize();
    } 
    catch (e) {
		GREUtils.log('[Error] GREUtils.File.normalize: '+e.message);
        rv = -1;
    }
    return rv;

};
/**
 *  XPCOM Directory Services
 *
 * @public
 * @name GREUtils.Dir
 * @namespace GREUtils.Dir
 */
GREUtils.define('GREUtils.Dir');

/**
 * Get File or Path ILocalFile Interface
 *
 * @public
 * @static
 * @function
 * @param {String} aPath
 * @return {nsILocalFile}
 */
GREUtils.Dir.getFile = function(aPath){
    var autoCreate = arguments[1] || false;
    if (/^file:/.test(aPath)) 
        aPath = aPath.replace("file://", "");
    var obj = GREUtils.XPCOM.createInstance('@mozilla.org/file/local;1', 'nsILocalFile');
    obj.initWithPath(aPath);
    if (obj.exists()) 
        return obj;
    else 
        if (autoCreate) {
            try {
                obj.create(GREUtils.File.DIRECTORY_TYPE, GREUtils.File.DIR_DEFAULT_PERMS);
                return obj;
            } 
            catch (ex) {
                return null;
            }
        }
        else {
            return null;
        }
};


/**
 * Create  Path and return ILocalFile Interface
 *
 * @public
 * @static
 * @function
 * @param {String} aPath
 * @return {nsILocalFile}
 */
GREUtils.Dir.create = function(aPath){
	return GREUtils.Dir.getFile(aPath, true); 
};


/**
 * remove Path
 *
 * @public
 * @static
 * @function
 * @param {String} aPath
 * @param {Boolean} aRecursive
 * @return {Number}
 */
GREUtils.Dir.remove = function(aPath, aRecursive){
	var dir = GREUtils.Dir.getFile(aPath);
	if(dir == null) return -1;
	
    if(!dir.isDirectory()) return -2; 
  	
	try {
		return dir.remove(aRecursive);	
	}catch (e){
		GREUtils.log('[Error] GREUtils.Dir.remove: '+e.message);
		return -3;
	}
};


/**
 * contains
 *
 * @public
 * @static
 * @function
 * @param {String} aPath
 * @param {String} aFile
 * @return {Boolean}
 */
GREUtils.Dir.contains = function(aPath, aFile){
	var dir = GREUtils.Dir.getFile(aPath);
	var file = GREUtils.File.getFile(aFile);
	
	if(dir == null || file == null) return false;
	
    if(!dir.isDirectory()) return false; 
	
	if(!dir.isFile()) return false;
  	
	try {
		return dir.contains(aFile, true);	
	}catch (e){
		GREUtils.log('[Error] GREUtils.Dir.contains: '+e.message);
		return false;
	}
};


/**
 * read entry directory
 *
 * @public
 * @static
 * @function
 * @param {Array}
 */
GREUtils.Dir.readDir = function(aPath){
	
	var fileInst = GREUtils.Dir.getFile(aPath);
    var rv = [];
	if (fileInst == null) return rv;
    
    try {
		
	  if (!fileInst.exists()) return rv;

      if (!fileInst.isDirectory()) return rv; 
  
      var files     = fileInst.directoryEntries;
      var file;
  
      while (files.hasMoreElements()) 
      {
        file = files.getNext();
		file = GREUtils.XPCOM.queryInterface(file, "nsILocalFile");
        
		if (file.isFile()) rv.push(file.path);
  
        if (file.isDirectory())
          rv.push(GREUtils.Dir.readDir(file.path));
      }
  
    } catch(e) {
		GREUtils.log('[Error] GREUtils.Dir.readDir: '+e.message);
	}
  
    return rv;
	
};
/**
 * XPCOM BASE Cryphto Hash Utilities
 * It is very faster then javascript implemention.
 *
 * @public 
 * @name GREUtils.CryptoHash
 * @namespace GREUtils.CryptoHash
 */
GREUtils.define('GREUtils.CryptoHash');

/**
 * can be used to compute a cryptographic hash function of some data.
 * You can, for example, calculate the MD5 hash of a file to determine if it contains 
 * the data you think it does. 
 * The hash algorithms supported are MD2, MD5, SHA-1, SHA-256, SHA-384, and SHA-512
 * 
 * @public
 * @static
 * @function 
 * @param {String} str
 * @param {String} algorithm
 * @return {String} crypted string
 */
GREUtils.CryptoHash.crypt = function(str, algorithm) {
	
	var converter =	GREUtils.XPCOM.getUsefulService('unicodeconverter');
	var cryptohash = GREUtils.XPCOM.getUsefulService('hash');
	
	converter.charset = "UTF-8";
	var result = {};
	// data is an array of bytes
	var data = converter.convertToByteArray(str, result);

	// init algorithm
	cryptohash.init(cryptohash[algorithm]);
	
	cryptohash.update(data, data.length);
	
	var hash = cryptohash.finish(false);
	
	// convert the binary hash data to a hex string.
	return GREUtils.CryptoHash.arrayToHexString(hash);
	
};

/**
 * can be used to compute a cryptographic hash function of some data.
 * You can, for example, calculate the MD5 hash of a file to determine if it contains 
 * the data you think it does. 
 * The hash algorithms supported are MD2, MD5, SHA-1, SHA-256, SHA-384, and SHA-512
 * 
 * @public
 * @static
 * @function  
 * @param {String} aFile
 * @param {String} algorithm
 * @return {String} crypted string
 */
GREUtils.CryptoHash.cryptFromStream = function(aFile, algorithm) {
	
	var cryptohash = GREUtils.XPCOM.getUsefulService('hash');

	var istream = GREUtils.File.getInputStream(aFile);
	
	if(GREUtils.isNull(istream)) return "";
	
	// init algorithm
	cryptohash.init(cryptohash[algorithm]);
	
	// this tells updateFromStream to read the entire file
	const PR_UINT32_MAX = 0xffffffff;
	cryptohash.updateFromStream(istream, PR_UINT32_MAX);

	// pass false here to get binary data back
	var hash = cryptohash.finish(false);

	// convert the binary hash data to a hex string.
	return GREUtils.CryptoHash.arrayToHexString(hash);

};


/**
 * calculate the MD5 hash of a string
 * 
 * @public
 * @static
 * @function  
 * @param {String} str
 * @return {String} hex md5 string
 */
GREUtils.CryptoHash.md5 = function(str) {

	return GREUtils.CryptoHash.crypt(str, "MD5");
};

/**
 * calculate the MD5 hash of a file
 * 
 * @public
 * @static
 * @function  
 * @param {String} aFile
 * @return {String} hex md5 string
 */
GREUtils.CryptoHash.md5FromFile = function(aFile){

	return GREUtils.CryptoHash.cryptFromStream(aFile, "MD5");
};

/**
 * calculate the MD5 hash of a file
 * 
 * @public
 * @static
 * @function  
 * @param {String} aFile
 * @return {String} hex md5string
 */
GREUtils.CryptoHash.md5sum = GREUtils.CryptoHash.md5FromFile;


/**
 * calculate the SHA-1 hash of a string
 * 
 * @public
 * @static
 * @function  
 * @param {String} str
 * @return {String} hex SHA1 string
 */
GREUtils.CryptoHash.sha1 = function(str) {

	return GREUtils.CryptoHash.crypt(str, "SHA1");
};


/**
 * calculate the SHA-256 hash of a string
 * 
 * @public
 * @static
 * @function  
 * @param {String} str
 * @return {String} hex SHA256 string
 */
GREUtils.CryptoHash.sha256 = function(str) {

	return GREUtils.CryptoHash.crypt(str, "SHA256");
};

/**
 * return the two-digit hexadecimal code for a byte
 * 
 * @public
 * @static
 * @function  
 * @param {String} charCode
 * @return {String} hex string
 */ 
GREUtils.CryptoHash.toHexString = function(charCode) {
  return ("0" + charCode.toString(16)).slice(-2);
};

/**
 * return the two-digit hexadecimal code for a Array
 * 
 * @public
 * @static
 * @function  
 * @param {Array} data
 * @return {String} hex string
 */ 
GREUtils.CryptoHash.arrayToHexString = function(data) {
  
  	// convert the binary hash data to a hex string.
	var s = [];
	for(var i in data) {
		s.push(GREUtils.CryptoHash.toHexString(data.charCodeAt(i)));
	}
	return s.join("");

};
/**
 * XPCOM Charset Convert / Unicode converter
 * 
 * @public
 * @name GREUtils.Charset
 * @namespace GREUtils.Charset
 */
GREUtils.define('GREUtils.Charset');

/**
 * Convert text from charset to Unicode String
 *
 * @public
 * @static
 * @function
 * @param {String} text
 * @param {String} charset
 * @return {String}
 */
GREUtils.Charset.convertToUnicode = function(text, charset) {
	
    try {
        var conv = GREUtils.XPCOM.getService("@mozilla.org/intl/scriptableunicodeconverter", "nsIScriptableUnicodeConverter");
        conv.charset = charset ? charset : "UTF-8";
        return conv.ConvertToUnicode(text);
    }catch (ex) {
		GREUtils.log('[Error] GREUtils.Charset.convertToUnicode: ' + ex.message);
        return text;
    }
	
};

/**
 * Convert Unicode String to specified charset.
 *
 * @public
 * @static
 * @function
 * @param {String} text
 * @param {String} charset
 * @return {String}
 */
GREUtils.Charset.convertFromUnicode = function(text, charset) {
    try {
        var conv = GREUtils.XPCOM.getService("@mozilla.org/intl/scriptableunicodeconverter", "nsIScriptableUnicodeConverter");
        conv.charset = charset ? charset : "UTF-8";
        return conv.ConvertFromUnicode(text);
    }catch (ex) {
		GREUtils.log('[Error] GREUtils.Charset.convertFromUnicode: '+ex.message);
        return text;
    }
};


/**
 * Convert Charset
 *
 * @public
 * @static
 * @function
 * @param {String} text
 * @param {String} in_charset
 * @param {String} out_charset
 * @return {String}
 */
GREUtils.Charset.convertCharset = function (text, in_charset, out_charset) {
    return this.convertFromUnicode(this.convertToUnicode(text, in_charset), out_charset);
};
/**
 *  XPCOM BASE Native JSON Services 
 *  
 *  It is very faster then javascript implemention.
 *  
 * @public 
 * @name GREUtils.JSON
 * @namespace GREUtils.JSON  
 */
GREUtils.define('GREUtils.JSON');

GREUtils.JSON = {
	_native: false,
	_jsonService: null
};


/**
 * Get Native JSON Service for High Performance.
 * 
 * Firefox3 or XULRunner 1.9 only
 * 
 * @public
 * @static
 * @function  
 * @return {Object}
 */
GREUtils.JSON.getJSONService = function() {
 	
	if (this._jsonService == null) {
		var jsonService = GREUtils.XPCOM.getUsefulService("json");
		if (jsonService) {
			this._native = true;
			this._jsonService = jsonService;
		}else {
			// use json javascript code
			this._native = false;
		}
	}
 	return this._jsonService;
};


/**
 * Decodes a JSON string, 
 * returning the JavaScript object it represents. 
 * 
 * @public
 * @static
 * @function 
 * @param {String} aJSONString
 * @return {Object}
 */
GREUtils.JSON.decode = function(aJSONString) {
 	return GREUtils.JSON.getJSONService().decode(aJSONString);
};


// formatJson() :: formats and indents JSON string
GREUtils.JSON.formatJson = function formatJson(val) {
	
    var retval = '';
    var str = val;
    var pos = 0;
    var strLen = str.length;
    var indentStr = '  ';
    var newLine = '\r\n';
    var mchar = '';

    for (var i=0; i<strLen; i++) {
        mchar = str.substring(i,i+1);
        
        if (mchar == '}' || mchar == ']') {
            retval = retval + newLine;
            pos = pos - 1;
            
            for (var j=0; j<pos; j++) {
                retval = retval + indentStr;
            }
        }
        
        retval = retval + mchar;    
        
        if (mchar == '{' || mchar == '[' || mchar == ',') {
            retval = retval + newLine;
            
            if (mchar == '{' || mchar == '[') {
                pos = pos + 1;
            }
            
            for (var k=0; k<pos; k++) {
                retval = retval + indentStr;
            }
        }
    }
    
    return retval;
};

/**
 * Encodes a JavaScript object into a JSON string.
 * 
 * @public
 * @static
 * @function 
 * @param {Object} aJSObject
 * @return {String} JSON string
 */
GREUtils.JSON.encode = function(aJSObject) {
 	return GREUtils.JSON.getJSONService().encode(aJSObject);
};


/**
 * Decodes a JSON string read from an input stream, 
 * returning the JavaScript object it represents. 
 * 
 * @public
 * @static
 * @function 
 * @param {Object} stream
 * @param {Object} contentLength
 * @return {Object} 
 */
GREUtils.JSON.decodeFromStream = function(stream, contentLength) {
	return GREUtils.JSON.getJSONService().decodeFromStream(stream, contentLength);
};


/**
 * Encodes a JavaScript object into JSON format, writing it to a stream. 
 * 
 * @public
 * @static
 * @function 
 * @param {Object} stream
 * @param {String} charset
 * @param {Boolean} writeBOM
 * @param {Object} value
 */
GREUtils.JSON.encodeToStream = function(stream, value, charset, writeBOM) {
	charset = charset || 'UTF-8';
	writeBOM = writeBOM || false;
	
	GREUtils.JSON.getJSONService().encodeToStream(stream, charset, writeBOM, value);
};


/**
 * Decodes a JSON string read from an local file, 
 * returning the JavaScript object it represents. 
 * 
 * @public
 * @static
 * @function 
 * @param {String} filename
 * @return {Object} 
 */
GREUtils.JSON.decodeFromFile = function(filename) {
    var fileInputStream = GREUtils.File.getInputStream(filename, "rb");
	if(fileInputStream == null) return null;
	
	// return GREUtils.JSON.decodeFromStream(fileInputStream, fileInputStream.available());

    // native json decodeFromStream buggy?
    // try to write self
    var aJSONString = GREUtils.File.readAllBytes(filename);
	aJSONString = GREUtils.Charset.convertToUnicode(aJSONString);
    return GREUtils.JSON.decode(aJSONString);

};


/**
 * Encodes a JavaScript object into JSON format, writing it to a local file. 
 * 
 * @public
 * @static
 * @function 
 * @param {Object} stream
 * @param {String} charset
 * @param {Boolean} writeBOM
 * @param {Object} value
 */
GREUtils.JSON.encodeToFile = function(filename, value) {
 
    var fileOutputStream = GREUtils.File.getOutputStream(filename, "w");
    if(fileOutputStream == null) return ;
    
    // GREUtils.JSON.encodeToStream(fileOutputStream, value);
    // native json decodeFromStream buggy?
    // try to write self
    var aJSONString = GREUtils.JSON.encode(value);
	aJSONString = GREUtils.Charset.convertFromUnicode(aJSONString, "UTF-8");
	aJSONString	= GREUtils.JSON.formatJson(aJSONString);
	GREUtils.File.writeAllBytes(filename, aJSONString);
    return;
};
/**
 *  Sound Services
 *  
 * @public 
 * @name GREUtils.Sound
 * @namespace GREUtils.Sound
 */
GREUtils.define('GREUtils.Sound');


/**
 * Get Sound Service
 * see  nsISound Interface document.
 *
 * @public
 * @static
 * @function 
 * @return {Object}
 *
 */
GREUtils.Sound.getSoundService = function() {
    return GREUtils.XPCOM.getUsefulService("sound");
};


/**
 * Play Sound by specified URL
 *
 * @public
 * @static
 * @function 
 * @param {String} sURL
 */
GREUtils.Sound.play = function(sURL) {
    mURL = GREUtils.File.getURL(sURL);
    var snd = GREUtils.Sound.getSoundService();
    snd.init();
    return snd.play(mURL);
};


/**
 * Play Sound Beep
 *
 * @public
 * @static
 * @function 
 */
GREUtils.Sound.beep = function() {
    return GREUtils.Sound.getSoundService().beep();
};


/**
 * Play System Sound by specified URL
 *
 * @public
 * @static
 * @function 
 * @param {String} sURL
 */
GREUtils.Sound.playSystemSound = function(sURL) {
    mURL = GREUtils.File.getURL(sURL);
    var snd = this.getSoundService();
    snd.init();
    return snd.playSystemSound(mURL);
};
/**
 *  XPCOM Preferences Services
 *  
 * @public 
 * @name GREUtils.Pref
 * @namespace GREUtils.Pref
 */
GREUtils.define('GREUtils.Pref');


/**
 * Get Application Preferences Service.
 *
 * see nsIPrefBranch2
 *
 * @public
 * @static
 * @function 
 * @return {Object}
 */
GREUtils.Pref.getPrefService = function () {
    return GREUtils.XPCOM.getService("@mozilla.org/preferences-service;1", "nsIPrefBranch2");
};


/**
 * Get Preference Value By Key.
 *
 * Auto Detect preference types.
 *
 * @public
 * @static
 * @function 
 * @param {String} prefName
 * @param {Object} PrefService
 * @return {Object}
 */
GREUtils.Pref.getPref = function() {
    var prefName = arguments[0] ;
    var prefs = (arguments[1]) ? arguments[1] : GREUtils.Pref.getPrefService();
    var nsIPrefBranch = GREUtils.XPCOM.Ci("nsIPrefBranch");
    var type = prefs.getPrefType(prefName);
    if (type == nsIPrefBranch.PREF_STRING)
        return prefs.getCharPref(prefName);
    else if (type == nsIPrefBranch.PREF_INT)
        return prefs.getIntPref(prefName);
    else if (type == nsIPrefBranch.PREF_BOOL)
        return prefs.getBoolPref(prefName);
};


/**
 * Set Preference Value By Key.
 *
 * Auto Detect preference types.
 *
 * @public
 * @static
 * @function 
 * @param {String} prefName
 * @param {Object} value
 * @param {Object} PrefService
 */
GREUtils.Pref.setPref = function() {
    var prefName = arguments[0] ;
    var value = arguments[1];
    var prefs = (arguments[2]) ? arguments[2] : GREUtils.Pref.getPrefService();
    var nsIPrefBranch = GREUtils.XPCOM.Ci("nsIPrefBranch");
    var type = prefs.getPrefType(prefName);
    if (type == nsIPrefBranch.PREF_STRING)
        prefs.setCharPref(prefName, value);
    else if (type == nsIPrefBranch.PREF_INT)
        prefs.setIntPref(prefName, value);
    else if (type == nsIPrefBranch.PREF_BOOL)
        prefs.setBoolPref(prefName, value);
};
/**
 *  XPCOM BASE Dialog Services 
 *  
 *  It can be use in JS XPCOM And JS Modules.
 *  
 * @public 
 * @name GREUtils.Dialog
 * @namespace GREUtils.Dialog   
 */
GREUtils.define('GREUtils.Dialog');

/**
 * openWindow USE nsIWindowWatcher is the keeper of Gecko/DOM Windows. 
 * It maintains a list of open top-level windows, and allows some operations on them.
 * 
 * GREUtils.Dialog can use in javascript code modules.
 * 
 * @param {Object} aParent
 * @param {String} aUrl
 * @param {String} aName
 * @param {String} aFeatures
 * @param {Object} aArguments
 */
GREUtils.Dialog.openWindow =  function(aParent, aUrl, aName, aFeatures, aArguments) {
	
	var parent = aParent || null;
	var name = aName || "_blank";
	var args = aArguments || null;
	var features = aFeatures || "chrome,centerscreen";
	
	var ww = GREUtils.XPCOM.getUsefulService("window-watcher");
	return ww.openWindow(null, aUrl, name, features, args);

};


/**
 * Open Dialog
 *
 * @public
 * @static
 * @function
 * @param {String} aUrl
 * @param {String} aName
 * @param {Object} aArguments
 * @param {Number} posX
 * @param {Number} posY
 * @param {Number} width
 * @param {Number} height
 */
GREUtils.Dialog.openDialog = function(aURL, aName, aArguments, posX, posY, width, height) {

    var features = "chrome,dialog,dependent=yes,resize=yes";
	if (arguments.length <= 3 ) {
		features += ",centerscreen";
	}
	else {
		if (posX) 
			features += ",screenX=" + posX;
		if (posY) 
			features += ",screenY=" + posY;
		if (width) 
			features += ",width=" + width;
		if (height) 
			features += ",height=" + height;
	}
	
	return GREUtils.Dialog.openWindow(null, aURL, aName, features, aArguments);

};


/**
 * Open Modal Dialog
 *
 * @public
 * @static
 * @function
 * @param {String} aUrl
 * @param {String} aName
 * @param {Object} aArguments
 * @param {Number} posX
 * @param {Number} posY
 * @param {Number} width
 * @param {Number} height
 */
GREUtils.Dialog.openModalDialog = function(aURL, aName, aArguments, posX, posY, width, height) {

    var features = "chrome,dialog,dependent=no,modal,resize=yes";	
	if (arguments.length <= 3) {
		features += ",centerscreen";
	}
	else {
	    if(posX) features += ",screenX="+posX;
	    if(posY) features += ",screenY="+posY;
	    if(width) features += ",width="+width;
	    if(height) features += ",height="+height;
	}
    
	return GREUtils.Dialog.openWindow(null, aURL, aName, features, aArguments);
	
};


/**
 * Open Full Screen Window
 *
 * @public
 * @static
 * @function
 * @param {String} aUrl
 * @param {String} aName
 * @param {Object} aArguments
 */
GREUtils.Dialog.openFullScreen = function (aURL, aName, aArguments) {
	
    var features = "chrome,dialog=no,resize=no,titlebar=no,fullscreen=yes";
    features += ",x=0,y=0";
    features += ",screenX="+0;
    features += ",screenY="+0;
	
	return GREUtils.Dialog.openWindow(null, aURL, aName, features, aArguments);
};


/**
 * Get File Picker
 *
 * see nsIFilePicker
 *
 * @public
 * @static
 * @function
 * @return {Object}
 */
GREUtils.Dialog.getFilePicker = function() {
    return GREUtils.XPCOM.getService("@mozilla.org/filepicker;1", "nsIFilePicker");
};

/**
 * Open File Picker Dialog
 *
 * @public
 * @static
 * @function
 * @param {String} sDir
 * @return {String}
 */
GREUtils.Dialog.openFilePicker = function(sDir){
    var filePicker = this.getFilePicker();
    if(sDir) {
        if (typeof(sDir)=="object" && GREUtils.XPCOM.queryInterface(sDir, "nsIFile")) {
            filePicker.displayDirectory = sDir;
        }
        if (typeof(sDir)=="string") {
            filePicker.displayDirectory = GREUtils.File.getFile(sDir);
        }
    }
    filePicker.show();
    return (filePicker.file.path.length > 0 ? filePicker.file.path : null);
};

/**
 * Alert Dialog
 * Can be use in XPCOM
 *
 * @public
 * @static
 * @function
 * @param {String} dialogTitle
 * @param {String} dialogText
 */
GREUtils.Dialog.alert = function(dialogTitle, dialogText) {
    // get a reference to the prompt service component.
    GREUtils.XPCOM.getUsefulService("prompt-service").alert(null, dialogTitle, dialogText);
};

/**
 * Confirm Dialog 
 * Can be use in XPCOM
 *
 * @public
 * @static
 * @function
 * @param {String} dialogTitle
 * @param {String} dialogText
 * @return {Boolean}
 */
GREUtils.Dialog.confirm = function(dialogTitle, dialogText) {
    // get a reference to the prompt service component.
    return GREUtils.XPCOM.getUsefulService("prompt-service").confirm(null, dialogTitle, dialogText);
};

/**
 * Prompt Dialog 
 * Can be use in XPCOM
 *
 * @public
 * @static
 * @function
 * @param {String} dialogTitle
 * @param {String} dialogText
 * @return {Boolean}
 */
GREUtils.Dialog.prompt = function(dialogTitle, dialogText, input) {
    // get a reference to the prompt service component.
    return GREUtils.XPCOM.getUsefulService("prompt-service").prompt(null, dialogTitle, dialogText, input);
};

/**
 * Prompt Select Dialog 
 * Can be use in XPCOM
 *
 * @public
 * @static
 * @function
 * @param {String} dialogTitle
 * @param {String} dialogText
 * @return {Boolean}
 */
GREUtils.Dialog.select = function(dialogTitle, dialogText, list, selected) {
    // get a reference to the prompt service component.
    return GREUtils.XPCOM.getUsefulService("prompt-service").select(null, dialogTitle, dialogText, list.length, list, selected);
};

/**
 * getMostRecentWindow returns a ChromeWindow object, or null, 
 * if there are no windows of a given type open. 
 * 
 * @public
 * @static
 * @function
 * @param {Object} windowName
 * @return {Object}
 */
GREUtils.Dialog.getMostRecentWindow = function(windowName) {
	return GREUtils.XPCOM.getUsefulService("window-mediator").getMostRecentWindow(windowName);
};

/**
 * enumerate all windows returns array of ChromeWindow object, or [], 
 * if there are no windows of a given type open. 
 * 
 * @public
 * @static
 * @function
 * @param {Object} windowName
 * @return {Object}
 */
GREUtils.Dialog.getWindowArray = function(windowName) {
	var enumerator = GREUtils.XPCOM.getUsefulService("window-mediator").getEnumerator(windowName);
	var wins = [];
	while(enumerator.hasMoreElements()) {
	  wins.push(enumerator.getNext());
	}
	return wins;	
};
/**
 * Thread - is simple and easy use Thread Manager APIs libraries for GRE (Gecko Runtime Environment).
 * ONLY Work with Firefox 3 or XULRunner 1.9
 * 
 * @public 
 * @name GREUtils.Thread
 * @namespace GREUtils.Thread 
 */
GREUtils.define('GREUtils.Thread');

GREUtils.Thread = {
    
    _threadManager: GREUtils.XPCOM.getUsefulService("thread-manager"),
    
    _mainThread: null,
    
    _workerThread: null,
    
    reportError: function(err){
        Components.utils.reportError(err);
    }
};


/**
 * getThreadManager 
 * 
 * @public
 * @static
 * @function 
 * @return {Object} nsIThreadManager 
 */
GREUtils.Thread.getThreadManager = function(){
    return this._threadManager;
};


/**
 * getMainThread
 *
 * @public
 * @static
 * @function 
 * @return {Object} nsIThread main thread 
 */
GREUtils.Thread.getMainThread = function(){
    if (this._mainThread == null) {
        this._mainThread = GREUtils.Thread.getThreadManager().mainThread;
        
        // extends magical method to worker thread
        // this._workerThread.dispatchMainThread = GREUtils.Thread.dispatchMainThread;
    }
    return this._mainThread;
};


/**
 * dispatchMainThread
 *
 * @public
 * @static
 * @function 
 * @return {Object} nsIThreadManager 
 * @param {Object} aRunnable
 * @param {Object} aType
 */
GREUtils.Thread.dispatchMainThread = function(aRunnable, aType) {
    var mainThread = GREUtils.Thread.getMainThread();
	var aType = aType || mainThread.DISPATCH_NORMAL;
    try {
	   mainThread.dispatch(aRunnable, aType);
	}catch (err) {
        GREUtils.Thread.reportError(err);
	}
};


/**
 * dispatchWorkerThread
 * 
 * @public
 * @static
 * @function 
 * @return {Object} nsIThreadManager 
 * @param {Object} workerThread
 * @param {Object} aRunnable
 * @param {Object} aType
 */
GREUtils.Thread.dispatchWorkerThread = function(workerThread, aRunnable, aType) {
    var aType = aType || workerThread.DISPATCH_NORMAL;
    try {
       workerThread.dispatch(aRunnable, aType);
    }catch (err) {
        GREUtils.Thread.reportError(err);
    }
};

/**
 * getWorkerThread in pool
 * 
 * @public
 * @static
 * @function 
 * @return {Object} nsIThread worker thread 
 */
GREUtils.Thread.getWorkerThread = function(){
    // get presist work thread 
    // will not create new worker thread
    if (this._workerThread == null) {
        this._workerThread = GREUtils.Thread.getThreadManager().newThread(0);
		
		// extends magical method to worker thread
        // this._workerThread.dispatchMainThread = GREUtils.Thread.dispatchMainThread;
    }
    return this._workerThread;
};


/**
 * createWorkerThread - create new worker thread.
 * 
 * @public
 * @static
 * @function 
 * @return {Object} nsIThread worker thread 
 */
GREUtils.Thread.createWorkerThread = function(){
    // create new worker thread
    var worker = GREUtils.Thread.getThreadManager().newThread(0);
	
	// extends magical method to worker thread
	//worker.dispatchMainThread = GREUtils.Thread.dispatchMainThread;
	
    return worker;
};


/**
 * CallbackRunnableAdapter
 *
 * @public
 * @class 
 * @param {Object} func
 * @param {Object} data
 */
GREUtils.Thread.CallbackRunnableAdapter = function(func, data) {
	this._func = func;
	this._data = data;
};

GREUtils.Thread.CallbackRunnableAdapter.prototype = {

        get func() {
            return this._func;
        },
        
        set func(func){
            this._func = func || null;
        },

        get data() {
            return this._data;
        },
        
        set data(data){
            this._data = data || null;
        },

        run: function() {
			try {
                 if (this.func) {
				 	if(this.data) this.func(this.data);
					else this.func();
				 }
             } catch (err) {
                Components.utils.reportError(err);
            }
        },
        
        QueryInterface: function(iid) {
            if (iid.equals(Components.Interfaces.nsIRunnable) || iid.equals(Components.Interfaces.nsISupports)) {
                return this;
            }
            throw Components.results.NS_ERROR_NO_INTERFACE;
        }
};


/**
 * WorkerRunnableAdapter
 *
 * @public
 * @class
 * @param {Object} func
 * @param {Object} callback
 * @param {Object} data
 */
GREUtils.Thread.WorkerRunnableAdapter = function(func, callback, data) {
    this._func = func;
	this._callback = callback;
    this._data = data;

    if(arguments.length == 2 ) {
        this._data = callback;
		this._callback = null;        
    }
};

GREUtils.Thread.WorkerRunnableAdapter.prototype = {

        get func() {
            return this._func;
        },
        
        set func(func){
            this._func = func || null;
        },

        get callback() {
            return this._callback;
        },
        
        set callback(callback){
            this._callback = callback || null;
        },

        get data() {
            return this._data;
        },
        
        set data(data){
            this._data = data || null;
        },

        run: function() {
            try {
				var result = null;
                 if (this.func) {
                    if(this.data) result = this.func(this.data);
                    else result = this.func();
                 }
				                
                if (this.callback) {
					GREUtils.Thread.dispatchMainThread(new GREUtils.Thread.CallbackRunnableAdapter(this.callback, result));
				}              
            } catch (err) {
                Components.utils.reportError(err);
            }

        },
        
        QueryInterface: function(iid) {
            if (iid.equals(Components.Interfaces.nsIRunnable) || iid.equals(Components.Interfaces.nsISupports)) {
                return this;
            }
            throw Components.results.NS_ERROR_NO_INTERFACE;
        }
};


/**
 * createWorkerThreadAdapter
 *
 * @public
 * @static
 * @function
 * @param {Object} workerFunc
 * @param {Object} callbackFunc
 * @param {Object} data
 */
GREUtils.Thread.createWorkerThreadAdapter = function(workerFunc, callbackFunc, data) {

    return new GREUtils.Thread.WorkerRunnableAdapter(workerFunc, callbackFunc, data);	
};
/*
 * GREUtils - is simple and easy use APIs libraries for GRE (Gecko Runtime Environment).
 *
 * Copyright (c) 2007 Rack Lin (racklin@gmail.com)
 *
 * $Date: 2007-09-16 23:42:06 -0400 (Sun, 16 Sep 2007) $
 * $Rev: 1 $
 */
/**
 *  GREUtils - is simple and easy use APIs libraries for GRE (Gecko Runtime Environment).
 * Controller and CommandDispatcher Helper
 */
GREUtils.ControllerHelper = GREUtils.extend({}, {

    /**
     * Append Controller to Window Controllers.
     * Then call Controller's init method
     *
     * @method
     * @id ControllerHelper.appendController
     * @alias GREUtils.ControllerHelper.appendController
     * @param {Object} controller
     */
    appendController: function(controller) {
        if(controller) window.controllers.appendController(controller);
        var app = arguments[1] || window;

        if(typeof(controller.init) == 'function') {
            controller.init(app);
        }
    },

    /**
     * Call CommandDispatcher to run Command By CommandName
     *
     * @method
     * @id ControllerHelper.doCommand
     * @alias GREUtils.ControllerHelper.doCommand
     * @param {String} sCmd
     */
    doCommand : function(sCmd) {
		try {
	        var cmdDispatcher = document.commandDispatcher || top.document.commandDispatcher || window.controllers;
	        var controller = cmdDispatcher.getControllerForCommand(sCmd);
	
	        if(controller) return controller.doCommand(sCmd);
	
	        // try window controller
	        controller = window.controllers.getControllerForCommand(sCmd);
	        if (controller && controller.isCommandEnabled(sCmd)) return controller.doCommand(sCmd);
		}catch(e){
			GREUtils.log('[Error] GREUtils.ControllerHelper.doCommand: '+e.message);
		}
    }

});

/**
 * ControllerAdapter
 *
 * @classDescription ControllerAdapter
 * @id ControllerAdapter
 * @alias GREUtils.ControllerAdapter
 */
GREUtils.ControllerAdapter = GREUtils.extend({}, {
    _app: null,
    _privateCommands: {'_privateCommands':1, '_app':1, 'init':1, 'supportsCommand':1, 'isCommandEnabled':1, 'doCommand':1, 'onEvent':1},

    /**
     * Controller Default Init method
     *
     * Normally don't need to override it.
     *
     * @method
     * @id ControllerHelper.init
     * @alias GREUtils.ControllerHelper.init
     * @param {Object} aApp
     */
    init : function(aApp) {
        this._app = aApp;
    },

    /**
     * Controller Support Command
     *
     * Normally not need to override it.
     *
     * @method
     * @id ControllerHelper.supportsCommand
     * @alias GREUtils.ControllerHelper.supportsCommand
     * @param {String} sCmd
     */
    supportsCommand: function(sCmd) {
        if( (!(sCmd in this._privateCommands)) && (sCmd in this) && typeof(this[sCmd]) == 'function' ) {
            return true;
        }
        return false;
    },

    /**
     * Controller isCommandEnabled
     *
     * @method
     * @id ControllerHelper.isCommandEnabled
     * @alias GREUtils.ControllerHelper.isCommandEnabled
     * @param {String} sCmd
     * @return {Boolean}
     */
    isCommandEnabled: function(sCmd) {
        return true;
    },

    /**
     * Controller doCommand
     *
     * Normally not need to override it.
     *
     * @method
     * @id ControllerHelper.doCommand
     * @alias GREUtils.ControllerHelper.doCommand
     * @param {String} sCmd
     */
    doCommand : function(sCmd) {
        if( (!(sCmd in this._privateCommands)) && (sCmd in this) && typeof(this[sCmd]) == 'function') {
            if(this.isCommandEnabled(sCmd)) return this[sCmd].call(this, arguments);
        }
    },

    /**
     * Controller onEvent
     *
     * Normally not need to override it.
     *
     * @method
     * @id ControllerHelper.onEvent
     * @alias GREUtils.ControllerHelper.onEvent
     * @param {String} sCmd
     */
    onEvent: function(sCmd) {
        if((sCmd in this) && typeof(this[sCmd]) == 'function') {
            if(this.isCommandEnabled(sCmd)) return this[sCmd].call(this, arguments);
        }
    }

});
