
/* Map impl */

function fade (target) {
      // create the <animation> element
      var animation = document.createElementNS('http://www.w3.org/2000/svg', 'animate');
      // set its attributes
      animation.setAttributeNS(null, 'attributeName', 'opacity');
      animation.setAttributeNS(null, 'from', 0);
      animation.setAttributeNS(null, 'to', 1);
      animation.setAttributeNS(null, 'dur', 1);
      animation.setAttributeNS(null, 'fill', 'freeze');
      // link the animation to the target
      target.appendChild(animation);
};

Ifpms.Map = {
_radius:13,
_cx:0,
_cy:15,
_idinfoX:1,
_idinfoY:25,
_idinfoFont:0,
_txtrectW:0,
_txtrectH:0,
_txtrectY:0,
_textNameX:0,
_textNameY:0,
_textNameFont:0,
_paiconR:(function(){ return getPaIcon();})(),
MapNode:function (xobj) {

    this.xobj = xobj;
    this.id = xobj.sid;
    this.status = NODE_STATUS_DISCONN;
    this.status_change_time = new Date();

    this.setStatus = function (status){
    
        var now = new Date()
	
        Components.utils.reportError(this.elem.id+", form "+this.status+" to "+status+", at:"+(now-this.status_change_time))
	
	if (this.status == status) {
	    this.status_change_time = new Date();
	    return;
	} else if( status < this.status) {
	    if ( (now-this.status_change_time) < 3000 ) {
		return;
	    }
	} else {
	}
	
        this.status = status;
	    this.status_change_time = new Date();
        this.elem.childNodes[0].setAttribute("class","device "+node_status_css_class[status]);    
        this.elem.childNodes[0].setAttribute("status",node_status_css_class[status]);

    };
    
    this.count=0;
    this.blinkLink=function(node){
       if(node.count%2==0){
            node.count++;
            node.elem.childNodes[0].setAttribute("class","device blink");
       }else{
            node.count++;
            node.elem.childNodes[0].setAttribute("class","device alarm_fiber_break");
       }
    };
    
    this.move = function (x,y){
        if(global_currentusertype > 0){
            var ewid=this.elem.childNodes[2].getAttribute('width');
            var min_pixel = 0;        
            if (x < min_pixel)
                x = min_pixel;
            if (x > Ifpms.Map._bgImageSize.w-min_pixel-ewid)
                x = Ifpms.Map._bgImageSize.w-min_pixel-ewid;
            if (y < min_pixel)
                y = min_pixel;
            if (y > Ifpms.Map._bgImageSize.h-min_pixel-48)
                y = Ifpms.Map._bgImageSize.h-min_pixel-48;

            this.elem.setAttribute("x", x);
            this.elem.setAttribute("y", y);

            this.xobj.cx = x;
            this.xobj.cy = y;
            Ifpms.Config.fresh();
        }
    };
    this.refresh=function()//刷新 节点 信息
    {
      $(this.elem.childNodes[3]).empty();
      var str=this.xobj.desc;
      if(str.length<1)
      {
         str=this.xobj.name;   
      }
      var bacwid=0;
      for(var i=0;i<str.length;i++)
      {
            if(str.charCodeAt(i)<128)
            {
                  bacwid+=10;
            }
            else{
                  bacwid+=18;
            }
      }
      bacwid=bacwid>40?bacwid:40;
	  bacwid+=2;
      this.elem.childNodes[2].setAttribute('width',bacwid*imgH/viewBoxH);
      this.elem.childNodes[0].setAttribute("cx",Ifpms.Map._cx*1.5);
      this.elem.childNodes[1].setAttribute("x",Ifpms.Map._cx);
      this.elem.childNodes[3].appendChild(document.createTextNode(str));
      this.move(this.xobj.cx,this.xobj.cy);//防止 调整尺寸后 节点不在地图范围之内
    };
    
    var imgW=Ifpms.Map._bgImageSize.w;
    var imgH=Ifpms.Map._bgImageSize.h;
    var viewBoxW=Ifpms.Map._viewBoxSize.w;
    var viewBoxH=Ifpms.Map._viewBoxSize.h;
    
    Ifpms.Map._cx=parseInt(22*imgH/viewBoxH);
    Ifpms.Map._cy=parseInt(29*imgW/viewBoxW);
    Ifpms.Map._radius=parseInt(Ifpms.Map._paiconR*imgH/viewBoxH);
    Ifpms.Map._txtrectW=parseInt(64*imgH/viewBoxH);
    Ifpms.Map._txtrectH=parseInt(20*imgW/viewBoxW);
    Ifpms.Map._txtrectY=parseInt(54*imgW/viewBoxW);
    Ifpms.Map._idinfoX=parseInt(10*imgW/viewBoxW);
    Ifpms.Map._idinfoY=parseInt(35*imgW/viewBoxW);
    Ifpms.Map._idinfoFont=parseInt(14*imgH/viewBoxH);
    Ifpms.Map._textNameX=parseInt(3*imgW/viewBoxW);
    Ifpms.Map._textNameY=parseInt(70*imgW/viewBoxW);
    Ifpms.Map._textNameFont=parseInt(18*imgH/viewBoxH);
    
    var elem = document.createElementNS("http://www.w3.org/2000/svg", "svg:svg");
    elem.setAttribute('version','1.1');  
    elem.setAttribute("id", "cricle-"+this.xobj.sid);
    elem.setAttribute("x",this.xobj.cx);
    elem.setAttribute("y",this.xobj.cy);
    elem.setAttribute("did",this.xobj.did);
	//elem.setAttribute('class','device');
    elem.setAttribute("status", "disable");
    //elem.setAttribute("cx", this.xobj.cx);
    
    var cir=document.createElementNS("http://www.w3.org/2000/svg", "svg:circle");
    cir.setAttribute('class','device');
	cir.setAttribute('r',Ifpms.Map._radius);
	cir.setAttribute('cx',Ifpms.Map._cx);
	cir.setAttribute('cy',Ifpms.Map._cy);
	cir.setAttribute("sid", this.xobj.sid);
    cir.setAttribute("did", this.xobj.did);
	elem.appendChild(cir);
	
	var idinfo=document.createElementNS("http://www.w3.org/2000/svg", "svg:text");
	idinfo.setAttribute("font-size",Ifpms.Map._idinfoFont);
	idinfo.setAttribute("stroke-width","1px");
	idinfo.setAttribute("x",Ifpms.Map._idinfoX);
	idinfo.setAttribute("y",Ifpms.Map._idinfoY);
	var str=this.xobj.did+'-'+this.xobj.pid;
	idinfo.appendChild(document.createTextNode(str));
	elem.appendChild(idinfo);
	
	var txrect=document.createElementNS("http://www.w3.org/2000/svg", "svg:rect");
	txrect.setAttribute('x',0);
	txrect.setAttribute('y',Ifpms.Map._txtrectY);
	//txrect.setAttribute('width',Ifpms.Map._txtrectW);
    txrect.setAttribute('height',Ifpms.Map._txtrectH);
    txrect.setAttribute('fill','#f0f0f0');
	txrect.setAttribute('style','opacity:0.5;');
	elem.appendChild(txrect);
    
	var txt=document.createElementNS("http://www.w3.org/2000/svg", "svg:text");
	txt.setAttribute("font-size",Ifpms.Map._textNameFont);
	txt.setAttribute("stroke-width","1px");
	txt.setAttribute('stroke','black');
	txt.setAttribute('fill','black');
    //txt.setAttribute('class','mapnodetxt');
	txt.setAttribute("x",Ifpms.Map._textNameX);
	txt.setAttribute("y",Ifpms.Map._textNameY);
    var des=this.xobj.desc;
    if(des.length<1)
    {
       des=this.xobj.name;
    }
    var charwidth=0;
    for(var i=0;i<des.length;i++)//计算背景 宽度
    {
        if(des.charCodeAt(i)<128)
        {
              charwidth+=10;
        }
       else{
            charwidth+=18;
        }
    }
	txt.appendChild(document.createTextNode(des));
	elem.appendChild(txt);
        charwidth=charwidth>40?charwidth:40;
		charwidth+=2;
        //alert(charwidth);
        elem.childNodes[0].setAttribute("cx",Ifpms.Map._cx*1.5);
        elem.childNodes[1].setAttribute("x",Ifpms.Map._cx);
        elem.childNodes[2].setAttribute("width",charwidth*imgH/viewBoxH);
	//elem.appendChild(document.createTextNode(this.xobj.sid));
       fade(elem.childNodes[0]);
    //var animate = document.createElementNS("http://www.w3.org/2000/svg", "svg:animate");
    //animate.setAttribute("attributeName", "r");
    //animate.setAttribute("from", "1");
    //animate.setAttribute("to", "12");
    //animate.setAttribute("dur", "1s");
    //animate.setAttribute("repeatCount", "indefinite");
    //elem.appendChild(animate);    
    if ( Ifpms.Map.svg ) {
        Ifpms.Map.svg.appendChild(elem);    
    } else {
        if (window.opener) {
          var map = window.opener.Ifpms.Map;
          if (map) {
            map.svg.appendChild(elem);
          }
       }
    }
    this.elem = elem;
    this.move(this.xobj.cx,this.xobj.cy);//防止初始位置 不在地图范围之内
    elem.addEventListener("mousedown", Ifpms.Map.mouseDown, false);
    return this;
},

_viewBoxSize : {w: 800,h:600},
_bgImageSize : {w: 800,h:600},
/* 缺省背景图片 */
//_bgImage : "chrome://ifpms/skin/images/map/default.png",
_bgImage:(function(){ return getMapImg();})(),
nodes : {},

/* 当前拖拽元素 */
draggingElement : null,
draggingNode : null,

/* Create svg and background image */
createSvgBox : function(_xul) {
    //jsdump("createBegin");
    this.xul = _xul;

    // create svg container
    this.svg = document.createElementNS("http://www.w3.org/2000/svg", "svg:svg");
    this.svg.setAttribute("version", "1.1");
    this.svg.setAttribute("id", "map");
    this.svg.setAttribute("width", this._viewBoxSize.w);
    this.svg.setAttribute("height", this._viewBoxSize.h);
    this.svg.setAttribute("viewBox", "0 0 "+this._bgImageSize.w+" "+this._bgImageSize.h);
    this.svg.setAttribute("preserveAspectRatio", "none"); //xMidYMax

    //create background image
    this.image = document.createElementNS("http://www.w3.org/2000/svg", "svg:image");
    this.image.setAttributeNS("http://www.w3.org/1999/xlink","xlink:href",this._bgImage);
    this.image.setAttribute("id","bgimage");
    this.image.setAttribute("x","0");
    this.image.setAttribute("y","0");
    this.image.setAttribute("opacity",0.6);
    this.image.setAttribute("width",this._bgImageSize.w);
    this.image.setAttribute("height",this._bgImageSize.h);

    this.svg.appendChild(this.image);
    this.xul.appendChild(this.svg);

    document.documentElement.addEventListener("mouseup", this.mouseUp, false);
    document.documentElement.addEventListener("mousemove", this.mouseMove, false);
    //jsdump("createEnd");
    window.setTimeout(this.bgImageReload, 10);

//    window.setInterval(this.flashlight, 400);

},
changeStatus : function(did, pid, status) {

        var o = 'PA-'+did+'-'+pid;
        var node = Ifpms.Map.nodes[o];
        if ( node.xobj.did == did && ( pid == 0 || node.xobj.pid == pid) && status != 7 && status != 8) {
            node.status = status;
            node.elem.childNodes[0].setAttribute("class","device " + node_status_css_class[status]);
            node.elem.childNodes[0].setAttribute("status",node_status_css_class[status]);
            if(status==4 || status==6){
                if(node.timer){
                    window.clearInterval(node.timer);
                }
                var nodefoo=Ifpms.Map.nodes[o];
                nodefoo.timer=window.setInterval(function(){
                    nodefoo.blinkLink(nodefoo);
                },100);
            }else{
                window.clearInterval(node.timer);
            }
        }
},

flashlight : function() {

    var now = new Date();
    for( var o in Ifpms.Map.nodes) {
	var node = Ifpms.Map.nodes[o];
	
	if ( node.status > NODE_STATUS_CONNECT ) {
	    /* 状态变化f超过一定时间，还原状态 */
	    if ((now-node.status_change_time) > 3000) {
		node.status = NODE_STATUS_DISCONN;
		node.elem.childNodes[0].setAttribute("class","device "+node_status_css_class[node.status]);
		node.elem.childNodes[0].setAttribute("status",node_status_css_class[node.status]);
		continue;
	    }
	    GREUtils.Sound.beep();
//	    Components.utils.reportError(node.elem.id+":device" + (now-node.status_change_time))
	    if(node.elem.childNodes[0].getAttribute("class").indexOf(node.elem.childNodes[0].getAttribute("status")) >= 0 ) {
		node.elem.childNodes[0].setAttribute("class","device");
//		Components.utils.reportError(node.elem.id+":device");
	    } else {
		node.elem.childNodes[0].setAttribute("class","device "+node.elem.childNodes[0].getAttribute("status"));    
//		Components.utils.reportError(node.elem.id+":device "+node.elem.getAttribute("status"));
	    }
	}
    }
},



bgImageReload : function() {
    var img = new Image();
    img.src = Ifpms.Map._bgImage;

    if( img.height == 0 || img.width == 0) {
        window.setTimeout(Ifpms.Map.bgImageReload, 50);
        delete img;
        return;       
    }
	
    var boxDeviceTree = document.getElementById("boxDeviceTree");
    var boxToolbar = document.getElementById("boxToolbar");
	
    var blankSpace = {}
    blankSpace.w = window.screen.width - boxDeviceTree.width - 30;
    blankSpace.h = window.screen.height - boxToolbar.height - 30;
    
    /* 保持背景图片的比例，则viewBox会有留白，判断上下或左右留白 */
/*
    if (  blankSpace.w /  blankSpace.h > img.width / img.height ) {
        blankSpace.w = blankSpace.h * img.width / img.height;
    } else {
        blankSpace.h = blankSpace.w * img.height / img.width;
    }
*/

    Ifpms.Map.svg.setAttribute("width", blankSpace.w);
    Ifpms.Map.svg.setAttribute("height", blankSpace.h);
    Ifpms.Map.svg.setAttribute("viewBox", "0 0 "+img.width+" "+img.height);
    Ifpms.Map.image.setAttribute("width",img.width);
    Ifpms.Map.image.setAttribute("height",img.height);

    Ifpms.Map._viewBoxSize.h = blankSpace.h;
    Ifpms.Map._viewBoxSize.w = blankSpace.w;
    Ifpms.Map._bgImageSize.h = img.height;
    Ifpms.Map._bgImageSize.w = img.width;

    

    delete img;
        
},

resize : function() {
    var sptMap = document.getElementById("sptMap");


    if (sptMap.getAttribute("state") == "collapsed" ) {
        var box_map = document.getElementById("boxMap")
        var rects = box_map.getClientRects();
        var height = rects[0].bottom - rects[0].top;
        var width = rects[0].right - rects[0].left;

//        jsdump("boxmap: "+width+"x"+height);
    
        Ifpms.Map.svg.setAttribute("width", width);
        Ifpms.Map.svg.setAttribute("height", height);
    } else {
        var boxDeviceTree = document.getElementById("boxDeviceTree");
        var boxToolbar = document.getElementById("boxToolbar");
        
        var blankSpace = {}
        if(boxDeviceTree.width<300){
            boxDeviceTree.width=350;
        }
        blankSpace.w = window.screen.width - boxDeviceTree.width - 30;
        blankSpace.h = window.screen.height - boxToolbar.height - 30;
        
        Ifpms.Map.svg.setAttribute("width", blankSpace.w);
        Ifpms.Map.svg.setAttribute("height", blankSpace.h);
    }

},

mouseDown : function (evt) {
    if(evt.currentTarget) {
        $('#map > [selected="true"]').attr("selected",false);
        Ifpms.Map.draggingElement = evt.currentTarget;
		Components.utils.reportError("Node:"+evt.currentTarget.getAttribute("id") + " "+ evt.currentTarget.childNodes[0].getAttribute("sid"));
        Ifpms.Map.draggingNode = Ifpms.Map.nodes[evt.currentTarget.childNodes[0].getAttribute("sid")];
        Ifpms.PaMgr.select(evt.currentTarget.childNodes[0].getAttribute("sid"));
        Ifpms.Map.draggingElement.parentNode.style.cursor='move';	
    }
},

mouseUp : function (evt) {
    if( Ifpms.Map.draggingElement) {
        document.getElementById("item-"+Ifpms.Map.draggingElement.childNodes[0].getAttribute("sid")).refresh();
        Ifpms.Map.draggingElement.parentNode.style.cursor='default';
        Ifpms.Map.draggingElement= false;
    }
},

mouseMove : function (evt) { 
    if(Ifpms.Map.draggingElement) {    
	var p= Ifpms.Map.draggingElement.parentNode.createSVGPoint();
	p.x = evt.clientX;
	p.y = evt.clientY;
    var m =Ifpms.Map.draggingElement.parentNode.getScreenCTM();
    p = p.matrixTransform(m.inverse());
    Ifpms.Map.draggingNode.move(p.x,p.y);//setAttribute("x",p.x);
    document.getElementById("item-"+Ifpms.Map.draggingElement.childNodes[0].getAttribute("sid")).refresh();
//	var device_loc_ele = document.getElementById("device_detail_loc");
//	device_loc_ele.setAttribute("value",parseInt(draggingElement.getAttribute("cx"))+":"+parseInt(draggingElement.getAttribute("cy")));

//        draggingElement.setAttribute("transform", "translate("+p.x+","+p.y+")");
    } else {
/*
	if (evt.target && evt.target.getAttribute("class") == "device") {
	    
	    var device_name_ele = document.getElementById("device_detail_name");
	    device_name_ele.setAttribute("value",evt.target.getAttribute("id"));
	    var device_loc_ele = document.getElementById("device_detail_loc");
	    device_loc_ele.setAttribute("value",parseInt(evt.target.getAttribute("cx"))+":"+parseInt(evt.target.getAttribute("cy")));
	    
	}
*/	
    }
}

};
function PA_observer()
{
 this.register();     
}
PA_observer.prototype={
      observe:function(subject,topic,data)
      {
            //alert(data);
            for(var i in Ifpms.Map.nodes)
            {
              Ifpms.Map.nodes[i].refresh();
            }
            //mgmt.ini();
            alarmmgmt.tablemanager.newestAlarmInit(5);
      },
     register:function()
     {
     var observerService = Components.classes["@mozilla.org/observer-service;1"]  
                          .getService(Components.interfaces.nsIObserverService);  
     observerService.addObserver(this, "PAchanged", false); 
     },
    unregister:function() {
    var observerService = Components.classes["@mozilla.org/observer-service;1"]  
                            .getService(Components.interfaces.nsIObserverService);  
    observerService.removeObserver(this, "PAchanged");  
   }   
}
Ifpms.Map.observer=new PA_observer();
Ifpms.Map.PAnotify=function(sid)
{
      var observerService_pa = Components.classes["@mozilla.org/observer-service;1"].  
      getService(Components.interfaces.nsIObserverService);
      var subject = Components.classes["@mozilla.org/supports-string;1"].  
      createInstance(Components.interfaces.nsISupportsString);  
      var data=sid;
      observerService_pa.notifyObservers(subject,"PAchanged", data);  
}


