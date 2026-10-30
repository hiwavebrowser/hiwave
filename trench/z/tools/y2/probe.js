try{var __s=function(n){if(!n)return null;if(n.nodeType===3)return '#t'+n.data.length;if(n.nodeType===8)return '#c:'+(n.data.length<5?n.data:'len'+n.data.length);return n.nodeName+(n.id?'#'+n.id:'')+(typeof n.className==='string'&&n.className?'.'+n.className.slice(0,50):'')};
var __r={fiberType:typeof e.type==='string'?e.type:String(e.tag),tag:e.tag,next:__s(rJ),nextParent:rJ&&__s(rJ.parentNode),
reactKids:function(){var o=[],c=e.child;while(c&&o.length<30){o.push(typeof c.type==='string'?c.type:(c.tag===6?'#text':'tag'+c.tag));c=c.sibling}return o}(),
domKids:function(){var o=[],k=e.stateNode&&e.stateNode.childNodes;for(var i=0;k&&i<k.length&&i<30;i++)o.push(__s(k[i]));return o}(),
props:Object.keys(e.memoizedProps||{}).slice(0,25),
chain:function(){var o=[],p=e.stateNode;while(p&&o.length<12){o.push(__s(p));p=p.parentNode}return o}(),
cookies:document.cookie.split(';').map(function(c){return c.split('=')[0].trim()})};
var __j=JSON.stringify(__r);for(var __i=0;__i<__j.length;__i+=450){console.error('Y2:'+__j.substr(__i,450))}}catch(__e){console.error('Y2FAIL '+__e)}
