function QuestionWebService() {
	this.c = "question";
};
QuestionWebService.prototype = {
	get_related_question : function(question_id, response_handler,callback_params) {
		this.send('get_related_question', {"question_id" : question_id}, response_handler,callback_params);
	},
	get_next_question : function(question_id,tags, response_handler,callback_params) {
		this.send('get_next_question', {"question_id" : question_id,"tags":tags}, response_handler,callback_params);
	},
	set_answer : function(question_id, answer,signature,response_handler,callback_params) {
		this.send('set_answer', {"question_id" : question_id,"answer" : answer,signature:signature}, response_handler,callback_params);
	},
	update : function(key, question_text,response_handler,callback_params) {
		this.send('update', {"key" : key,"question_text" : question_text}, response_handler,callback_params);
	},
	update_status : function(key, status,response_handler,callback_params) {
		this.send('update_status', {"key" : key,"status" : status}, response_handler,callback_params);
	},
	update_answer : function(key, answer_text,response_handler,callback_params) {
		this.send('update_answer', {"key" : key,"answer_text" : answer_text}, response_handler,callback_params);
	},
	delete_question : function(key,response_handler,callback_params) {
		this.send('delete', {"key" : key}, response_handler,callback_params);
	},
	delete_category : function(key,tag,response_handler,callback_params) {
		this.send('delete_category', {"key" : key,"tag":tag}, response_handler,callback_params);
	},
	add_category : function(key,tag,response_handler,callback_params) {
		this.send('add_category', {"key" : key,"tag":tag}, response_handler,callback_params);
	},
	create : function(question_text,answer_text,tags,sentence_key,question_type,response_handler,callback_params) {
		this.send('create', {"question_text" : question_text,"tags":tags,"answer_text":answer_text,"sentence_key":sentence_key,"question_type":question_type}, response_handler,callback_params);
	},
	fibcreate : function(question_text,answer_text,tags,sentence_key,response_handler,callback_params) {
		this.send('fibcreate', {"question_text" : question_text,"tags":tags,"answer_text":answer_text,"sentence_key":sentence_key}, response_handler,callback_params);
	},
	set_sentence_status:function(status,sentence_key,response_handler,callback_params) {
		this.send('set_sentence_status', {"status":status,"sentence_key":sentence_key}, response_handler,callback_params);
	}
};
QuestionWebService.prototype.__proto__ = WebService.prototype;
