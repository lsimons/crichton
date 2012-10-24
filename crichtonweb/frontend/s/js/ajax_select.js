# Crichton, Admirable Source Configuration Management
# Copyright 2012 British Broadcasting Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#
/*
File copied from ajax_selects (http://code.google.com/p/django-ajax-selects/)
which is dual-licensed under the GPL and the MIT license. Use here is under
the MIT license.
Added by Leo Simons for the BBC.

Copyright (c) 2009 Chris Sattinger. Copyright (c) 2011 BBC.
All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/
/* requires RelatedObjects.js */

function didAddPopup(win,newId,newRepr) {
    var name = windowname_to_id(win.name);
    $("#"+name).trigger('didAddPopup',[html_unescape(newId),html_unescape(newRepr)]);
    win.close();
}

// based on http://code.google.com/p/django-ajax-selects/issues/detail?id=50

function setup_autocompleteselect($, me, url) {
	(function ($, me, url) {
		var me_selector       = "#" + me;
		var text_id           = me + "_text";
		var text_selector     = "#" + text_id;
		var on_deck_id        = me + "_on_deck";
		var on_deck_selector  = "#" + on_deck_id;
		var kill_id           = "kill_" + me;
		var kill_selector     = "#"  + kill_id;
		
		var functions = Object();
		functions.kill = function() {
			$(me_selector).val('');
			$(on_deck_selector).children().fadeOut(1.0).remove();
		};
		functions.addKiller = function(repr) {
			if ($(kill_selector).length > 0) {
				return;
			}
			var kill = '<span class="iconic" id="' + kill_id + '">X</span>';
			if (repr) {
				$(on_deck_selector).empty();
				var html = "<div>" + kill + repr + "</div>";
				$(on_deck_selector).append(html);
			} else {
				$(on_deck_selector + " > div").prepend(kill);
			}
			$(kill_selector).click(function() {
				functions.kill();
				$(on_deck_selector).trigger("killed");
			});
		};
		functions.receiveResult = function(event, ui) {
			prev = $(me_selector).val();
			if(prev) {
				functions.kill(prev);
			}
			$(me_selector).val(ui.item.id);
			$(text_selector).val("");
			functions.addKiller(ui.item.value, ui.item.id);
			$(on_deck_selector).trigger("added");
		};
		functions.emptyResultText = function(event, ui) {
			// this is really annoying... $(text_selector).val("");
		};
	
		$(text_selector).autocomplete({
			source: url,
			select: functions.receiveResult,
			close: functions.emptyResultText,
			//minLength: 3,
		});
		if($(me_selector).val()) { // add X for initial value if any
			functions.addKiller(null);
		}
		$(me_selector).bind('didAddPopup',function(event,id,repr) {
			ui = Object();
			ui.item = Object();
			ui.item.id = id;
			ui.item.value = repr;
			functions.receiveResult(null,ui);
		});
	})($, me, url);
}

var autocompleteselectmultiplevalues = new Array();

function setup_autocompleteselectmultiple($, me, url) {
	(function ($, me, url) {
		var currentRepr = autocompleteselectmultiplevalues[me];
		
		var me_selector       = "#" + me;
		var text_id           = me + "_text";
		var text_selector     = "#" + text_id;
		var on_deck_id        = me + "_on_deck";
		var on_deck_selector  = "#" + on_deck_id;
		var kill_id           = "kill_" + me;
		var kill_selector     = "#"  + kill_id;
		
		var functions = Object();
		functions.kill = function(item_id) {
			var item_selector = on_deck_selector + "_"+ item_id;
			var val = $(me_selector).val();
			val = val.replace( "|" + item_id + "|", "|" );
			$(me_selector).val(val);
			$(item_selector).fadeOut().remove();
		}
		functions.addKiller = function(repr, item_id) {
			var item_kill_id = kill_id + "_" + item_id;
			var item_kill_selector = kill_selector + "_" + item_id;
			var kill = '<span class="iconic"" id="' + item_kill_id + '">X</span>';
			var html = '<div id="' + item_kill_id +  '">' + kill + repr + " </div>"
			$(on_deck_selector).append(html);
			$(item_kill_selector).click(function(frozen_id) {
				return function() {
					functions.kill(frozen_id);
					$(on_deck_selector).trigger("killed");
				}
			}(item_id));
		}
		functions.receiveResult = function(event, ui) {
			var item_id = ui.item.id;
			if($(me_selector).val().indexOf("|" + item_id + "|") == -1) {
				var val = $(me_selector).val()
				if(val == '') {
					val = '|';
				}
				val += item_id + "|";
				$(me_selector).val(val);
				functions.addKiller(ui.item.value, item_id);
				$(on_deck_selector).trigger("added");
			}
		}
		functions.emptyResultText = function(event, ui) {
			// this is really annoying... $(text_selector).val("");
		};
		
		$(text_selector).autocomplete({
			source: url,
			select: functions.receiveResult,
			close: functions.emptyResultText,
			//minLength: 3,
		});
		$.each(currentRepr, function(i,its) {
			repr = its[0];
			item_id = its[1]
			functions.addKill(repr, item_id);
		});
		$(me_selector).bind('didAddPopup',function(event,id,repr) {
			ui = Object();
			ui.item = Object();
			ui.item.id = id;
			ui.item.value = repr;
			functions.receiveResult(null,ui);
		});
	})($, useid, url);
}
