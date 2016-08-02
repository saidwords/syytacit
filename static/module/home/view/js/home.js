function HomeController() {
	var webservice = new ArticleWebService();
	var data={
		tags:[],
		user: {username:false}	 
	};
	var ui={
		article_search_form:$('article_search_form'),
		search:$('#search'),
		approve_link:$('.approve'),
		reject_link:$('.reject'),
		
		init:function(){
			//ui.search.keypress(controller.search);
			ui.article_search_form.click(controller.search);
			ui.approve_link.each(function( index ) {
				$(this).click(controller.approve_article);
			});
			ui.reject_link.each(function( index ) {
				$(this).click(controller.reject_article);
			});
			$(document).bind('LOGGEDIN', function(e,userObj) {	
				data.user.username=userObj.username;
			});
			$(document).bind('LOGGEDOUT', function(e,userObj) {	
				data.user.username=false;
			});
		},
		update_article_approval_count :function(article_key,delta){
			if (delta=="0"){
				return false;
			}
			var el=$('#article_numapprovals_'+article_key);
			var numapprovals=parseInt(el.html());
			
			numapprovals=numapprovals+parseInt(delta);
			
			el.html(numapprovals);
			
		}
	};
	
	var controller={
		init:function(){
			ui.init();
		},
		search:function(event){
			ui.article_search_form.submit();
		},
		approve_article:function(){
			if(data.user.username==false){
				$(this).callout(
						{position:"left",msg:"You must be logged in"}
				).mouseleave(function() { 
					$(this).callout("destroy"); 
				});
				return false;
			}
			
			$(this).addClass("ajaxcircle");
			$(this).css('color',$(this).css('background-color'));
			webservice.approve_article($(this).data("key"),ajaxhandlers.approve_article,$(this));
		},
		
		reject_article:function(){
			if(data.user.username==false){
				$(this).callout(
						{position:"left",msg:"You must be logged in"}
				).mouseleave(function() { 
					$(this).callout("destroy"); 
				});
				return false;
			}
			
			$(this).addClass("ajaxcircle");
			$(this).css('color',$(this).css('background-color'));
			webservice.reject_article($(this).data("key"),ajaxhandlers.reject_article,$(this));
		}
	};
	
	var ajaxhandlers={
		search:function(response,callback_params){
			console.log(response);
		},
		approve_article:function(response,callback_params){
			callback_params.removeClass("ajaxcircle");
			callback_params.css("background-color:#ffffff;");
			
			if(response.exception==null){
				$('#article_controls_'+callback_params.data('key')).html('{ approved }');
				ui.update_article_approval_count(response.article_key,response.delta)
				
			}else{
				callback_params.callout({position:"left",msg:response.exception.message}).mouseenter(function() { 
					$(this).callout("destroy"); 
				});
				
			}
			
		},
		reject_article:function(response,callback_params){
			callback_params.removeClass("ajaxcircle");
			callback_params.css("background-color:#ffffff;");
			
			if(response.expetion!=null){
				callback_params.callout({position:"left",msg:response.exception.message});
			}else{
				//ui.update_article_approval_count(response.article_key,response.delta)
				
				$('#article_controls_'+callback_params.data('key')).html('{ rejected }');
				
			}
			setTimeout(function(){callback_params.callout("destroy");},3000);
		}
	};
	
	return {
		init: controller.init,
		data:data
	};
};

function ArticleWebService() {
	this.c = "article";
};
ArticleWebService.prototype = {
	approve_article:function(article_key,response_handler,response_params) {
		this.send('approve', {"article_key" : article_key,"approve":true}, response_handler,response_params);
	},
	reject_article:function(article_key,response_handler,response_params) {
		this.send('reject', {"article_key" : article_key,"approve":false}, response_handler,response_params);
	},
	search:function(terms,response_handler,response_params) {
		this.send('search', {"terms" : terms}, response_handler,response_params);
	}
};
ArticleWebService.prototype.__proto__ = WebService.prototype;