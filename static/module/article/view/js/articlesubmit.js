function ArticleSubmitController() {
	var webservice = new ArticleSubmitWebService();
	var data={
		tags:[],
		user:{username:false}
	};
	var ui={
		article_submitter:$('#article_submitter'),
		article_title:$('#article_title'),
		new_article_title:$('#new_article_title'),
		original_article_title:$('#original_article_title'),
		article_description:$('#article_description'),
		new_article_description:$('#new_article_description'),
		original_article_description:$('#original_article_description'),
		article_url:$('#article_url'),
		new_article_url:$('#new_article_url'),
		article_form: $('#article_form'),
		new_article_url: $('#new_article_url'),
		article_tags: $('#article_tags'),
		new_article_tags: $('#new_article_tags'),
		btn_submit_article:$('#btn_submit_article'),
		post_target:$('.post_target'),
		post_target_community:$('#post_target_community'),
		post_target_url:$('#post_target_url'),
		message:$('#message'),
		new_article_url_container:$('#new_article_url_container'),
		community_container:$('#community_container'),
		community:$('#community'),
		
		init:function(){
		
			ui.post_target_community.click(function(){
				ui.new_article_url_container.hide();
				//ui.community_container.show();
			});
			ui.post_target_url.click(function(){
				ui.new_article_url_container.show();
				//ui.community_container.hide();
			});
		
			ui.btn_submit_article.click(function(){
				controller.submit_article();
			});
			//ui.tags.change(controller.set_tags);
			
			ui.new_article_url.blur(function(){
				post_target=null;
				ui.post_target.each(function(index){
					if($(this).attr('checked')=='checked'){
						post_target=$(this).val();
					}
				});
				if(post_target=='url' && ui.new_article_url.val().length>1){
					ui.original_article_title.html("fetching article title...");
					ui.original_article_description.html("fetching article description...");
					webservice.getArticleMeta(ui.new_article_url.val(),ajaxhandlers.getArticleMeta);
				}
			});
			ui.new_article_url.change(function(){	
				ui.article_url.html(ui.new_article_url.val());
				ui.article_url.attr('href',ui.new_article_url.val());
			});
			ui.new_article_url.keyup(function(){	
				ui.article_url.html(ui.new_article_url.val());
			});
			ui.new_article_title.keyup(function(){
				ui.article_title.html(ui.new_article_title.val());
			});
			ui.new_article_description.keyup(function(){	
				ui.article_description.html(ui.new_article_description.val());
			});
			ui.new_article_title.change(function(){
				ui.article_title.html(ui.new_article_title.val());
			});
			/*
			ui.new_article_tags.keyup(function(){	
				ui.article_tags.html(ui.new_article_tags.val());
			});
			ui.new_article_tags.change(function(){	
				ui.article_tags.html(ui.new_article_tags.val());
			});
			*/
			ui.new_article_description.change(function(){	
				ui.article_description.html(ui.new_article_description.val());
			});
			
		
			
		},
		templates: {
			response_form: $.template("response_form", "<textarea rows=5 cols=32></textarea>")
		}
	};
	
	var controller={
		init:function(){
			ui.init();
			$(document).bind('LOGGEDIN', function(e,user) {	
				ui.article_submitter.html(user.user.username);
				ui.message.html('');
				ui.btn_submit_article.attr("disabled",false);
				ui.new_article_url.attr("disabled",false);
			});
			
			if(data.user.username==false){
				ui.message.html("You must be logged in");
				ui.btn_submit_article.attr("disabled", "disabled");
				ui.new_article_url.attr("disabled", "disabled");
			}
		},
		submit_article:function(){
			
			post_target=null;
			ui.post_target.each(function(index){
				if($(this).attr('checked')=='checked'){
					post_target=$(this).val();
				}
			});
			if(post_target=='community'){
				if(ui.community.val()==""){
					ui.btn_submit_article.callout({position:"right",msg:'community is required'}).mouseenter(function() { 
						$(this).callout("destroy"); 
					});
					return false;
				}
			}else{
				if(ui.new_article_url.val()==""){
					ui.btn_submit_article.callout({position:"right",msg:'url is required'}).mouseenter(function() { 
						$(this).callout("destroy"); 
					});
					return false;
				};
				if(ui.new_article_title.val()=="" && ui.original_article_title.html()==""){
					ui.btn_submit_article.callout({position:"right",msg:'title is required'}).mouseenter(function() { 
						$(this).callout("destroy"); 
					});
					return false;
				}
			}
			
			ui.btn_submit_article.html("&nbsp;&nbsp;Submitting");
			ui.btn_submit_article.addClass("ajaxcircle");
			
			webservice.submit_article(ui.new_article_title.val(),ui.new_article_url.val(),ui.new_article_description.val(),ui.original_article_title.html(),ui.original_article_description.html(),null,post_target,ui.community.val(),ajaxhandlers.submit_article);
		},
		set_tags:function(){
			data.tags=ui.tags.val().split(' ');
		}
	};
	
	var ajaxhandlers={
		submit_article:function(response){
			ui.btn_submit_article.html("&nbsp;&nbsp;Submit");
			ui.btn_submit_article.removeClass("ajaxcircle");
			
			if(response.exception!=null && response.exception!=""){
				if(response.exception.type=='DuplicateUrl'){
					response.exception.message="Url has already been submitted here: <a href='"+response.url+"'>"+response.url+'</a>';
				}
				ui.btn_submit_article.callout({position:"right",msg:response.exception.message}).mouseenter(function() { 
					$(this).callout("destroy"); 
				});
			}else{
				ui.btn_submit_article.callout({position:"right",msg:"Article submitted"}).mouseenter(function() { 
					$(this).callout("destroy"); 
				});
				post_target=null;
				ui.post_target.each(function(index){
					if($(this).attr('checked')=='checked'){
						post_target=$(this).val();
					}
				});
				if(post_target=='community'){
					ui.article_title.attr('href','/community/'+ui.community.val()+'/'+response.article.ihref);
				}else{
					ui.article_title.attr('href','/article/detail/'+response.article.ihref);
				}
				ui.article_url.html(response.article.href);
				ui.article_url.attr('href',response.article.href);
			}
		},
		getArticleMeta:function(response){
			//ui.new_article_title.attr("placeholder","");
			//ui.new_article_description.attr("placeholder","");
			if(response.exception!=null){
				ui.new_article_url.callout({position:"right",msg:response.exception.message}).click(function() { 
					$(this).callout("destroy"); 
				});
				return;
			}
			
			ui.original_article_title.html(response.title);
			ui.article_title.html(response.title);
			ui.original_article_description.html(response.description);
			ui.article_description.html(response.description);
		}
	};
	
	return {
		init: controller.init,
		data:data
	};
};

function ArticleSubmitWebService() {
	this.c = "article";
	this.cache={"foo":1};
};
ArticleSubmitWebService.prototype = {
	submit_article:function(title,url,description,original_title,original_description,tags,post_target,category,response_handler) {
		this.send('save', {"title" : title,"url":url,"description":description,"original_title":original_title,"original_description":original_description,"tags":tags,"post_target":post_target,"category":category}, response_handler);
	},
	getArticleMeta:function(url,response_handler){
		var cache=this.cache;
		
		if(cache[url] !=undefined){
			return response_handler(cache[url]);
		}
		
		if(url.length>3){
			this.send('get_article_meta',{"url":url},function(response){
				cache[url]=response;
				response_handler(response);
			});
		}
	}
	
};
ArticleSubmitWebService.prototype.__proto__ = WebService.prototype;