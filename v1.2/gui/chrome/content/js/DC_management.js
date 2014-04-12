var  global_show_obj_DC;//当前 显示的 DC对象信息
var global_show_obj_PA;//PA信息
var global_show_DC_PA;//当前显示的是DC还是PA
var global_DC_list=[];//系统中所有DC组成的列表
var global_edit_DC_PA;
var DCmgmt_ini=function()//进入DC管理界面的初始化 函数 
{

Refresh_DC_info();
}
function DC_Class()
{
this.did="dc1";
this.number="---";
this.ipaddr="192.168.0.108";
this.macaddr="FEEFEFFEf";
this.name="dcc";
this.desc="desc";
this.enableflag="关闭";
this.cx='122';
this.cy='233';
this.status="status";
this.lastest_change_time="2011-8-9";
this.product_type="type";
this.pa_number='3';
this.product_ID="d";
this.hw_version="1.0";
this.sw_version="0.5";
this.palist=[];     
}

function PA_Class()
{    
this.pid="pa1";
this.did="dc1";
this.number="0";
this.name="0";
this.desc="0";
this.cx="0";
this.cy="0";
this.enableflag='关闭';
this.status="0";
this.mediumlength="0";
this.alarmseverity="0";
this.alarmsensitivity='0';
this.workmode='0';
this.windfactor="0";
}

function Refresh_DC_info (){
    var emptydc;
    show_DC_detail(emptydc);//
    global_show_DC_PA=-1;
    global_edit_DC_PA=-1;
    global_DC_list.splice(0,global_DC_list.length);
  for(di=0;di<Ifpms.Xpcom.DCMgmt.dc_list.length;di++)
  {
    var tdc=Ifpms.Xpcom.DCMgmt.dc_list.queryElementAt(di,Components.interfaces.nsIPyIfpmsDC);
    var dc=new DC_Class();
    dc.did=tdc.did;
    dc.name=tdc.name;
    dc.desc=tdc.desc;
    dc.number=tdc.sid;
    dc.ipaddr=tdc.ipaddr;
    dc.macaddr=tdc.mac;
    dc.cx=tdc.cx;
    dc.cy=tdc.cy;
    dc.enableflag=tdc.enable;
    dc.status=tdc.status;
    dc.lastest_change_time=tdc.latest_change_time
    dc.product_type=tdc.product_type
    dc.pa_number=tdc.pa_num;
    dc.product_ID=tdc.product_id
    dc.hw_version=tdc.hw_version;
    dc.sw_version=tdc.sw_version;
    dc.mediumtype=tdc.medium_type;
    dc.sensitivity=tdc.sensitivity;
    dc.sensitivity2=tdc.sensitivity2;
    dc.environmentfactor=tdc.env_factor;
    for(var i=0;i<Ifpms.Xpcom.DCMgmt.pa_list.length; i++)
    {
             var pa = Ifpms.Xpcom.DCMgmt.pa_list.queryElementAt(i,Components.interfaces.nsIPyIfpmsPA);
             if(pa.did==dc.did)
             {
                var tpa=new PA_Class();
                    tpa.did=pa.did; tpa.number=pa.sid; tpa.pid=pa.pid;
                    tpa.cx=pa.cx; tpa.cy=pa.cy; tpa.name=pa.name;
                    tpa.desc=pa.desc;
                    tpa.enableflag=pa.enable;
                    tpa.status=pa.status;
                    tpa.mediumlength=pa.medium_len;
                    tpa.alarmsensitivity=pa.alarm_sensitivity;
                    tpa.alarmseverity=pa.alarm_severity;
                    tpa.windfactor=pa.wind_factor;
                    tpa.workmode=pa.work_mode;
                    tpa.enable_start=pa.enable_start;
                    tpa.enable_end=pa.enable_end;
                    dc.palist.push(tpa);
             }        
    }
        global_DC_list.push(dc);    
  }
       clear_DC();//清空原有DC
       for (d in global_DC_list)
       {    
            append_dc(global_DC_list[d],global_DC_list[d].palist);    
       }
}

function append_dc(newdc,newpa)//在DC tree 中 增加一个DC 以及对应 PA
{
var topc=document.getElementById("topchildren");
var dc=document.createElement("treeitem");
var dcrow=document.createElement("treerow");
var dc_icon=document.createElement("treecell");
  dc_icon.setAttribute("properties","item_dc");
  dcrow.appendChild(dc_icon);
var cel=document.createElement("treecell");  
    cel.setAttribute("label",newdc.did);
    dcrow.appendChild(cel);
var cel2=document.createElement("treecell");
    cel2.setAttribute("label","--");
    dcrow.appendChild(cel2);
var cel3=document.createElement("treecell");
    cel3.setAttribute("label",newdc.number);
    dcrow.appendChild(cel3);
    dc.appendChild(dcrow);
if(newpa.length>0)//防区 
{
dc.setAttribute("container",true);
dc.setAttribute("open",false);
var pac=document.createElement("treechildren");
for(i=0;i<newpa.length;i++)//加载每个防区
{
    var pa=document.createElement("treeitem");
    var parow=document.createElement("treerow");
    var pa_icon=document.createElement("treecell");
    pa_icon.setAttribute("properties","item_pa");
    parow.appendChild(pa_icon);
    var pacel=document.createElement("treecell");    
    pacel.setAttribute("label",newpa[i].did);    
    parow.appendChild(pacel);
    var pacel2=document.createElement("treecell");
    pacel2.setAttribute("label",newpa[i].pid);
    parow.appendChild(pacel2);
    var pacel3=document.createElement("treecell");
    pacel3.setAttribute("label",newpa[i].number);
    parow.appendChild(pacel3);
    pa.appendChild(parow);
    pac.appendChild(pa);
}
dc.appendChild(pac);
}
   topc.appendChild(dc);  
}

function clear_DC()//清空所有  DC
{
    var topc=document.getElementById("topchildren");
    for(i=topc.childNodes.length-1;i>=0;i--)
    {
       topc.removeChild(topc.childNodes[i]); 
    }
}

function show_DC_detail(obj_dc){ 
grid_DC_show_detail();
document.getElementById("DC_info").setAttribute("style","color:black;background:white;border:1px gray solid;-moz-border-radius: 10px;display:;");
document.getElementById("PA_info").setAttribute("style","color:black;background:white;border:1px gray solid;-moz-border-radius: 10px;display:none");
if(obj_dc==undefined)//未定义
{
    var ids=[];
    ids.push("did","number","ipaddr","macaddr","enableflag","name","desc","cx","cy","status");
    ids.push("lastest_change_time","product_type","pa_number","product_ID");
    ids.push("hw_version","sw_version","mediumtype","sensitivity","sensitivity2","environmentfactor");
    for (i in ids){
        document.getElementById("dc_label_"+ids[i]).setAttribute("value","");
    }    
}
else{
    var strbun=document.getElementById("dc_management_str");
    var newvalues=new Array(strbun.getString("coated"),strbun.getString("hang1"),strbun.getString("hang2"),strbun.getString("hang3"),strbun.getString("hang4"));
    newvalues.push(strbun.getString("hang5"),strbun.getString("underground1"),strbun.getString("underground2"),strbun.getString("underground3"),strbun.getString("underground4"));
    document.getElementById("dc_label_"+"mediumtype").value=newvalues[obj_dc.mediumtype];    
    document.getElementById("dc_label_"+"sensitivity").value=obj_dc.sensitivity;
    document.getElementById("dc_label_"+"sensitivity2").value=obj_dc.sensitivity2;
    document.getElementById("dc_label_"+"environmentfactor").value=obj_dc.environmentfactor;
    for (var i in obj_dc)
    {
        if(i!='palist')
        {
          document.getElementById("dc_label_"+i).setAttribute("value",obj_dc[i]);
        }
        
    }
}
grid_DC_show_detail();   
}

function show_PA_detail(obj_pa){    
document.getElementById("PA_info").setAttribute("style","color:black;background:white;border:1px gray solid;-moz-border-radius: 10px;display:;");
document.getElementById("DC_info").setAttribute("style","color:black;background:white;border:1px gray solid;-moz-border-radius: 10px;display:none");
if(obj_pa==undefined)
{    
 var ids=[];
 ids.push("pid","did","name","desc","enableflag","cx","cy","status");//,"mediumtype");
 ids.push("mediumlength","alarmseverity","windfactor","alarmsensitivity","workmode");//"sensitivity","sensitivity2","environmentfactor"
for(i in ids)
{
    document.getElementById("pa_label_"+ids[i]).setAttribute("value","");
}
}
else{
    for(i in obj_pa)
    { 
        if(i!='enable_start'&&i!='enable_end')
        {
          document.getElementById("pa_label_"+i).setAttribute("value",obj_pa[i]);
        }
        
    }
 }
  var enabletimestr=obj_pa.enable_start+':00--'+obj_pa.enable_end+':00'; 
  document.getElementById('pa_label_enablehours').value=enabletimestr;   
  grid_PA_show_detail();
}

function fetch_DC_obj(dc_id)// 根据did 获得 dc 对象
{
    var res={};
    res.flag=false;
    for (i in global_DC_list)
    {
        if(global_DC_list[i].did==dc_id)
        {
            res.dc=global_DC_list[i];
            res.flag=true;
        }
    }        
    return res;
}

function fetch_PA_obj(dc_id,pa_id)//获得 pa 对象
{
    var res={};
    res.flag=false;
    for(d in global_DC_list)
    {
        if(global_DC_list[d].did==dc_id)
        {
            for (p in global_DC_list[d].palist)
            {
                if(global_DC_list[d].palist[p].pid==pa_id)
                {
                    res.pa=global_DC_list[d].palist[p];
                    res.flag=true;
                }             
            }      
        }
    }
    return res;    
}