function Category() {
	var webservice = new CategoryWebService();
	var data={
			page:1,
			haswikiname:false
	};
	var ui = {
		prevlink : $('#prevlink'),
		nextlink : $('#nextlink'),
		haswikiname: $('#haswikiname'),
		catnames:$('input[id^="catname-"]'),
		wikinames:$('input[id^="wikiname-"]'),
		init : function() {
			ui.updatepagination();
			ui.haswikiname.change(ui.updatepagination);
			ui.wikinames.change(controller.mapwikiname);
		},
		updatepagination:function(){
			if(ui.haswikiname.attr("checked")=='checked'){
				ui.prevlink.attr("href","/category/browse/"+(data.page-1)+"/true");
				ui.nextlink.attr("href","/category/browse/"+(data.page+1)+"/true");		
			}else{
				ui.prevlink.attr("href","/category/browse/"+(data.page-1));
				ui.nextlink.attr("href","/category/browse/"+(data.page+1));
			}
			
		}
	};
	
	var controller= {
		mapwikiname:function(){
			var a=$(this).attr("id");
			var b=a.split('-');
			var c='#catname-'+b[1];
			console.log(c)
			var d=$(c);
			
			webservice.setwikiname(d.val(),$(this).val());
			
		}
	};

	return {
		data : data,
		init : ui.init
	};

};

function CategoryWebService() {
	this.c = "category";
};
CategoryWebService.prototype = {
		setwikiname:function(name, wikiname,response_handler) {
		this.send('setwikiname', {name:name,wikiname:wikiname}, response_handler);
	}
};
CategoryWebService.prototype.__proto__ = WebService.prototype;