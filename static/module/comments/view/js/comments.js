function Commentscontroller() {
	var webservice = new CommentsWebService();
	var data = {
		comment_key:0,
		stack : [],
		article_key : 0,
		comment : {
			rank : 0,
			id : 0,
			text : ""
		},
		user : {
			username:false,
			isadmin:false
		},
		responses : [],
		page : 0,
		limit : 10,
		parent_key : null,
		maxlevels : 3
	};
	var ui = {
		btn_save_comment : $('#btn_save_comment'),
		foo : null,
		comment : $('#comment'),
		comments : $('#comments'),
		more_comments : $('#more_comments'),
		children : $('#children'),

		init : function() {
		
			
			ui.btn_save_comment.click(function() {
				controller.savecomment(data.article_key, ui.comment.val(), null,ui.btn_save_comment, ui.children);
			});
			ui.more_comments.data('page', 1);
			ui.more_comments.data('comment_key',data.comment_key)
			ui.more_comments.data('el_container',ui.comments);
			ui.more_comments.click(controller.get_more_comments);
			
		},
		
		display_comment_form : function(ev) {

			if (data.user.username == false) {
				$(this).callout({
					position : "left",
					msg : "you must be logged in"
				}).mouseleave(function() {
					$(this).callout("destroy");
				});
				return;
			}
			// if the form is already displayed then dont display it again
			var comment = $(this).data('comment');
			var parent = $(this).data('parent');
			var children = $(this).data('children');
			var found = false;

			for ( var i = 0; i < data.responses.length; i++) {
				if (data.responses[i] == comment) {
					found = true;
					data.responses[i].response_container.show();
				}
			}
			if (found == false) {
				data.responses.push(comment);
				var response_container = $('<div></div>');
				var response_form = $('<textarea class="response_form" rows=5 cols=80></textarea>');
				var save_button = $('<button>save</button>');

				response_form.appendTo(response_container);
				save_button.appendTo(response_container);

				// response_form.appendTo(parent);
				// save_button.appendTo(parent);
				response_container.appendTo(parent);
				comment.response_container = response_container;
				
				save_button.click(function(ev) {
					if(response_form.val()==""){
						return;
					}
					response_container.hide();
					// TODO: set a valid comment id in the following function so
					// that users can respond to their own comments.
					// response_html=ui.construct_thread_html({comment:response_form.val(),comment_key:null,user:user,responses:[]});
					// response_html.prependTo(children);
					
					// controller.savecomment(data.article_key,response_form.val(),comment.comment_key,parent,response_form,children,response_form.val());
					controller.savecomment(data.article_key,response_form.val(), comment.comment_key, parent,children);
				});

			}

		},
		render_comments : function(responses,el_container) {
			
			var html = $('<div class="comment" ></div>');
			ui.children = $('<div class="children"></div>');

			for ( var i = 0; i < responses.length; i++) {
				response_html = ui.construct_thread_html(responses[i],0,null);
				response_html.appendTo(ui.children);
			}

			ui.children.appendTo(html);
			html.appendTo(el_container);
			
		},
		construct_thread_html : function(comment, level,parent_comment) {
			if (comment.comment_key == 0 || comment.comment_key=="") {
				return;
			}
			var html = $('<div class="comment-box"></div>');
			var comment_html = $('<div itemprop="comment" class="comment" data-key='+comment.comment_key+'>' + comment.comment+ '</div>');
		
			var comment_meta = $('<div class="comment_meta">&#8211;' + '<a itemprop="creator" href="/user/home/'+comment.username+'">'+comment.username+'</a> on '+comment.date+'</div>');
			comment_meta.appendTo(comment_html);
			comment_html.appendTo(html);
			var children = $('<div class="children"></div>');
			
			var controls = $('<div class="controls"></div>');
			controls.prependTo(comment_meta);
			
			var open_parens=$('<span>{</span>');
			open_parens.appendTo(controls);
			
			if(comment.username==data.user.username || data.user.isadmin){
				;// dont let the user react to his own comment
				var delete_comment=$('<a>delete</a>');
				delete_comment.click(controller.delete_comment);
				delete_comment.appendTo(controls);
			}else{
				
				var respond = $('<a>respond</a>');
				respond.appendTo(controls);
				respond.data('comment', comment);
				respond.data('parent', comment_html);
				respond.click(ui.display_comment_form);
				
				if(comment.approved=='1'){
					var approve = $('<span class="approved">| approved</span>');
				}else if(comment.approved=='0'){
					var approve = $('<span class="rejected">| rejected</span>');
				}else{
					var approve = $('<a data-key="'+comment.comment_key+'"> approve </a>');
					approve.data('comment', comment);
					approve.click(controller.approvecomment);
					
					var reject = $('<a data-key="'+comment.comment_key+'"> reject </a>');
					reject.appendTo(controls);
					reject.data('comment', comment);
					reject.click(controller.rejectcomment);
					reject.data('approve_link',approve);
					approve.data('reject_link',reject);
				}
				
				approve.appendTo(controls);
				respond.data('children', children);
			}
			
			var close_parens=$('<span>}</span>');
				close_parens.appendTo(controls);
			comment_html.data('parent_comment', parent_comment);
			
			var highlight = $('<a> ⋮ </a>');
			highlight.appendTo(comment_meta);
			
			highlight.click(function(ev){
				var bgcolor=comment_html.css('background-color')
				if(bgcolor=="rgb(210, 210, 210)"){
					bgcolor='rgb(232, 232, 232)';
				}else{
					bgcolor="rgb(210, 210, 210)";
				}
				ui.toggle_highlight(comment_html,bgcolor);
			});
			
			for ( var i = 0; i < comment.responses.length; i++) {
				response_html = ui.construct_thread_html(comment.responses[i],level + 1,comment_html);
				if(response_html!=null){
					response_html.appendTo(children);
				}
			}
			children.appendTo(html);
			return html;
		},
		toggle_highlight: function(el,bgcolor){
			el.css('background-color',bgcolor);
			pc=el.data("parent_comment");
			if(pc!=null){
				ui.toggle_highlight(pc,bgcolor);
			}
		},
		update_article_comment_count :function(article_key,delta){
			if (delta=="0"){
				return false;
			}
			var el=$('#article_numcomments_'+article_key);
			var numcomments=parseInt(el.html());
			
			numcomments=numcomments+parseInt(delta);
			
			el.html(numcomments);
			
		},
		templates : {
			response_form : $.template("response_form","<textarea class='response_form' rows=5 cols=32></textarea>")
		}
	};

	var controller = {
		init : function() {
		 $(document).bind('LOGGEDIN', function(e,userObj) {
			 data.user.username=userObj.username;
		 }); 
		 $(document).bind('LOGGEDOUT', function(e,userObj) {	
	         data.user.username=false;
		 });
		 ui.init();

		},
		getcomments: function(){
			if(data.comment_key !=null){
				webservice.getcomments(data.comment_key, 5,data.page,data.limit, ajaxhandlers.getcomments,{'el_container':ui.comments});	
			}
		},
		savecomment : function(article_key, comment, parent_key, el_actor,el_container) {
		
			if(data.user.username == false){
			
				el_actor.callout({
					position : "right",
					msg : "you must be logged in"
				}).mouseleave(function() {
					el_actor.callout("destroy");
				});
			
			
				return;
			}
		
			webservice.savecomment(article_key, comment, parent_key,ajaxhandlers.savecomment, {
				comment : comment,
				parent_key : parent_key,
				el_actor : el_actor,
				el_container : el_container
			});
		},
		delete_comment : function() {
			var r=confirm("Are you sure you want to delete the comment?");
			if(!r){
				return false;
			}
			var comment=$(this).closest('.comment');
			var key = comment.data('key');
			webservice.deletecomment(key, ajaxhandlers.deletecomment,{comment:comment});
		},
		get_more_comments : function() {
			var page=$(this).data('page');
			var comment_key=$(this).data('comment_key');
			var handler_params={
		//		comment : comment,
				el_container : $(this).data('el_container'),
				button: $(this)
			}
			
			webservice.getcomments(comment_key,data.maxlevels, page, data.limit,ajaxhandlers.getcomments,handler_params);
			page++;
			$(this).data('page',page);
		},
		approvecomment: function(){
			if (data.user.username == false) {
				$(this).callout({
					position : "left",
					msg : "you must be logged in"
				}).mouseleave(function() {
					$(this).callout("destroy");
				});
				return;
			}
			
			var comment=$(this).data('comment');
			$(this).addClass("ajaxcircle");
			$(this).css('color',$(this).css('background-color'));
			webservice.approve(data.article_key,comment.comment_key,true,ajaxhandlers.approvecomment,{el_actor:$(this)});
		},
		rejectcomment: function(){
			if (data.user.username == false) {
				$(this).callout({
					position : "left",
					msg : "you must be logged in"
				}).mouseleave(function() {
					$(this).callout("destroy");
				});
				return;
			}
			
			var comment=$(this).data('comment');
			$(this).addClass("ajaxcircle");
			$(this).css('color',$(this).css('background-color'));
			webservice.approve(data.article_key,comment.comment_key,false,ajaxhandlers.rejectcomment,{el_actor:$(this)});
		}
	};	

	var ajaxhandlers = {
		savecomment : function(response, params) {
			if (response.exception!=null && response.exception!="") {
				params.el_actor.callout({
					position : "right",
					msg : response.exception.message
				}).mouseleave(function() {
					$(this).callout("destroy");
				});
			} else {
				ui.update_article_comment_count(data.article_key,response.delta)
			
				var response_html = ui.construct_thread_html({
					comment : params.comment,
					date:response.date,
					comment_key : response.comment_key,
					username : response.user.username,
					responses : []
				});
				if(response_html!=null){
					response_html.prependTo(params.el_container);
				}
				
			}
		},
		deletecomment : function(response, params) {
			if (response.exception!=null && response.exception!="") {
				params.comment.callout({
					msg : response.exception.message,
					position : "top"
				}).mouseleave(function() {
					$(this).callout("destroy");
				});
				return;
			}
		
			ui.update_article_comment_count(data.article_key,response.delta)
			params.comment.callout({
				msg : "your comment has been deleted",
				position : "right"
			}).mouseleave(function() {
				$(this).callout("destroy");
			});
			
			params.comment.html("deleted");
				
		},
		getcomments : function(response, params) {
			if (response.exception != null && response.exception!="") {
				alert(response.exception.message);
				return;
			}
			if(response.responses.length>0){
				ui.render_comments(response.responses,params.el_container);
			}else{
				// remove the 'more comments' link
				$( "<span>no more comments found</span>" ).replaceAll( ui.more_comments );
				//ui.more_comments.remove();
			}
			
		},
		approvecomment: function(response,params){
			params.el_actor.removeClass("ajaxcircle");
			params.el_actor.css("color","#909090");
			if(response.exception!=null && response.exception!=""){
				params.el_actor.callout({
					msg : response.exception.message,
					position : "top"
				}).mouseleave(function() {
					$(this).callout("destroy");
				});
				return false;
			}
			
			params.el_actor.addClass("disabled");
			params.el_actor.data('reject_link').html("");
			params.el_actor.data('reject_link').addClass("disabled");
			params.el_actor.html(" approved");
			
			
		},
		rejectcomment: function(response,params){
			params.el_actor.removeClass("ajaxcircle");
			params.el_actor.css("color","#909090");
			if(response.exception!=null && response.exception!=""){
				params.el_actor.callout({
					msg : response.exception.message,
					position : "top"
				}).mouseleave(function() {
					$(this).callout("destroy");
				});
				return false;
			}
			
			params.el_actor.addClass("disabled");
			params.el_actor.data('approve_link').html("");
			params.el_actor.data('approve_link').addClass("disabled");
			params.el_actor.html(" rejected");
				
		}
	};

	return {
		init : controller.init,
		data : data,
		getcomments : controller.getcomments
	};

};

function CommentsWebService() {
	this.c = "comments";
};
CommentsWebService.prototype = {
	getcomments : function(comment_key, maxlevels, page, limit,response_handler,response_handler_params) {
		this.send('getcomments', {
			"comment_key" : comment_key,
			"maxlevels" : maxlevels,
			"page" : page,
			"limit" : limit
		}, response_handler,response_handler_params);
	},
	savecomment : function(article_key, comment, parent_key, response_handler,response_handler_params) {
		this.send('savecomment', {
			"article_key" : article_key,
			"comment" : comment,
			"parent_key" : parent_key
		}, response_handler, response_handler_params);
	},
	deletecomment : function(comment_key, response_handler,response_handler_params) {
		this.send('delete', {
			"comment_key" : comment_key,
		}, response_handler,response_handler_params);
	},
	approve:function(article_key,comment_key,approve,response_handler,response_handler_params){
		this.send('approve', {
			"article_key" : article_key,
			"comment_key" : comment_key,
			"approve" : approve
		}, response_handler,response_handler_params);
	}
	
};
CommentsWebService.prototype.__proto__ = WebService.prototype;