    function displayMainMenu(){
    	//alert('uff');
      if(jQuery('#menu_admin').length != 0){
      	loadMainMenu(jQuery('#menu_admin'), true);
      	loadSubMenu(jQuery('#configure'), false);
      	loadMainMenu(jQuery('#menu_orgadmin'), false);
      	loadMainMenu(jQuery('#menu_faculty'), false);
      	loadMainMenu(jQuery('#menu_user'), false);
      }
      else if(jQuery('#menu_orgadmin').length != 0){
      	loadMainMenu(jQuery('#menu_orgadmin'), true);
      	loadMainMenu(jQuery('#menu_faculty'), false);
      	loadMainMenu(jQuery('#menu_user'), false);
      }
      else if(jQuery('#menu_faculty').length != 0){
      	loadMainMenu(jQuery('#menu_faculty'), true);
      	loadMainMenu(jQuery('#menu_user'), false);
      }
      else if(jQuery('#menu_user').length != 0){
      	loadMainMenu(jQuery('#menu_user'), true);
      }else
      {
      	$.cookie('menu_admin', null, {path: '/' });
      	$.cookie('menu_orgadmin', null, {path: '/' });
      	$.cookie('menu_faculty', null, {path: '/' });
      	$.cookie('menu_user', null, {path: '/' });
      	$.cookie('configure', null, {path: '/' });
      }
    }
    
    function loadMainMenu(obj, show){
    	loadMenu(obj, obj.parent().siblings(), show);
    }

    function loadSubMenu(obj, show){
    	loadMenu(obj, obj.siblings(), show);    
    }

    function loadMenu(obj, children, show){
    	obj_id = obj.attr('id');
    	is_visible = $.cookie(obj_id);
    	if(is_visible == 'true'){
    		children.show();
    	}else if(is_visible == 'false'){
    		children.hide();
    	}else{
    		if(show){
    			children.show();
    		}else{
    			children.hide();
    		}
    	}
    	addToCookie(obj, children);
    }

    function addToMainCookie(obj){
    	addToCookie(obj, obj.parent().siblings())
    }

    function addToSubCookie(obj){
    	addToCookie(obj, obj.siblings())
    }
	
    function addToCookie(obj, children){
    	obj_id = obj.attr('id');
    	is_visible = children.is(':visible');
    	$.cookie(obj_id, is_visible, {path: '/' });
    }
    
    function tab_refresh(){
    	$.cookie('tab_index',$("#tabs-task").tabs('option', 'active'));
    }
