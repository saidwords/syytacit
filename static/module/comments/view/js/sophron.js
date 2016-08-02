function Sophron() {
	var data={
		stack:[]
	};
	var ui={
		comments:null,
		top_comment:null,
		init:function(stack){
			data.stack=stack;
			ui.comments=$('.comment');
			ui.top_comment=data.stack[0];
			var viewport=util.getPageScroll();
			var position=ui.top_comment.position();
			
			$(window).scroll(function(ev){
				//TODO: when the topmost comment is almost scrolled out of the viewport, then lock it into place and set the first child as the next subject
			    position=ui.top_comment.position();
			    viewport=util.getPageScroll();
			     if(position.top <= viewport[1]){
			    	//TODO: push the locked comment onto the locked comment stack
			    	ui.lock_comment();
			     }else if(position.top > viewport[1]){
			    	ui.unlock_comment();
			     }
			     //TODO: if the locked comment needs to be unlocked the pop the locked comment stack
				// the top pixel in the viewport is at viewport[1];
				console.log(position.top +','+ viewport[1]);
				
			});
		},
		lock_comment:function(){
			ui.top_comment.css('position','fixed');
			ui.top_comment.css('top','5px');
			data.stack.push(ui.top_comment);
			ui.top_comment=data.stack[1];//wtf is the next comment?
		},
		unlock_comment:function(){
			ui.top_comment.css('position','relative');
			ui.top_comment.css('top','');
			ui.top_comment=data.stack.pop();
		}
	};
	
	var util={
		getPageScroll: function() {
			var xScroll, yScroll;
			if (self.pageYOffset) {
				yScroll = self.pageYOffset;
				xScroll = self.pageXOffset;
			} else if (document.documentElement && document.documentElement.scrollTop) {
				yScroll = document.documentElement.scrollTop;
				xScroll = document.documentElement.scrollLeft;
			} else if (document.body) {// all other Explorers
				yScroll = document.body.scrollTop;
				xScroll = document.body.scrollLeft;
			}
			return [xScroll,yScroll]
		},
		findPos: function(obj) {
			var curleft = curtop = 0;
			if (obj.offsetParent) {	
				do {
					curleft += obj.offsetLeft;
					curtop += obj.offsetTop;	
				} while (obj = obj.offsetParent);
			}
			return [curleft,curtop];
		}
	};
	
	return {
		init:ui.init
	};
};