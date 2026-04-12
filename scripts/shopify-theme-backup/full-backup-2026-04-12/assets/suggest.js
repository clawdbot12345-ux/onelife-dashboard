(function( $ ) {
  'use strict';
   if ($('.nt-products-suggest').length == 0 || ($(window).width() < 768 && !NTsuggest.onMobile) ) return;
   var $wrap = $('.nt-products-suggest'),
       min = 0,random = 0,ranLocation = 0,ranTime=0,StayTime=0,StarTime=NTsuggest.start_time * NTsuggest.start_time_unit,nt_check = false,max = NtHandleArr.length - 1;
    //sales popup for the first time
    setTimeout(function () { 
      loadSalesPopup(); 
    }, StarTime );
   //Loads sales popup
    function loadSalesPopup() {
      if (nt_check) return;
         StayTime= NTsuggest.stay_time * NTsuggest.stay_time_unit;
         ranLocation = Math.floor(Math.random() * (NtLoctionArr.length - 1 - min + 1)) + min,
         ranTime = Math.floor((Math.random() * 60) + 1);
        if(NTsuggest.type==1){
         SequentialSalesPopUp();      
        }else{
         RandomSalesPopUp();
        }
        setTimeout(function() {
            unloadSalesPopup();
        }, StayTime);
   }
   //unLoads sales popup
   function unloadSalesPopup() {
      var x = NTsuggest.range_from * 1;
      var y = NTsuggest.range_to * 1;
      var PopRange= Math.floor((Math.random() * (y-x)) + x + 1) * 1000;
      hideSlaesPopUp();
      setTimeout(function(){
       //$('#nt__suggest').html(''); 
       loadSalesPopup();
      }, StarTime);
   }
   function RandomSalesPopUp() {
      random = Math.floor(Math.random() * (max - min + 1)) + min;
      var data_url = $('#nt__suggest').attr("data-url")+NtHandleArr[random],
          img_url = NtimgArr[random].replace(".jpg?v=", "_90x.jpg?v=").replace(".png?v=", "_90x.png?v=").replace(".gif?v=", "_90x.gif?v="),
          img_url2 = NtimgArr[random].replace(".jpg?v=", "_90x@2x.jpg?v=").replace(".png?v=", "_90x@2x.png?v=").replace(".gif?v=", "_90x@2x.gif?v=");
      //console.log(data_url)
      preload([img_url,img_url2]);
      $('#nt__suggest .img_suggest').attr('src', img_url);
      $('#nt__suggest .img_suggest').attr('srcset', img_url+' 1x, '+img_url2+' 2x');
      $('#nt__suggest .suggest-qv').attr('data-ajax', data_url+'/?view=quick_view'); 
      $('#nt__suggest .table_suggest a').attr('href', data_url);
      $('#nt__suggest .product-title').html(NtTitleArr[random]); 
      $('#nt__suggest .minute-number').html(ranTime);
      $('#nt__suggest .from').html(NtLoctionArr[ranLocation]);
      showSlaesPopUp();
      $( 'body' ).on( 'click', '.suggest-close', function(e) {
          e.preventDefault();
          setTimeout(function() {
             unloadSalesPopup();
             nt_check = true;
         }, 100);
      });
   }
   function preload(arrayOfImages) {
      $(arrayOfImages).each(function(){
          $('<img/>')[0].src = this;
          // Alternatively you could use:
          // (new Image()).src = this;
      });
  }
   function SequentialSalesPopUp() {
      ++random;
      if (random > NtHandleArr.length) {random = 1}
      var data_url = $('#nt__suggest').attr("data-url")+NtHandleArr[random-1],
          img_url = NtimgArr[random-1].replace(".jpg?v=", "_90x.jpg?v=").replace(".png?v=", "_90x.png?v=").replace(".gif?v=", "_90x.gif?v="),
          img_url2 = NtimgArr[random-1].replace(".jpg?v=", "_90x@2x.jpg?v=").replace(".png?v=", "_90x@2x.png?v=").replace(".gif?v=", "_90x@2x.gif?v=");
      //console.log(data_url)
      preload([img_url,img_url2]);
      $('#nt__suggest .img_suggest').attr('src', img_url);
      $('#nt__suggest .img_suggest').attr('srcset', img_url+' 1x, '+img_url2+' 2x');
      $('#nt__suggest .suggest-qv').attr('data-ajax', data_url+'/?view=quick_view'); 
      $('#nt__suggest .table_suggest a').attr('href', data_url);
      $('#nt__suggest .product-title').html(NtTitleArr[random-1]); 
      $('#nt__suggest .minute-number').html(ranTime);
      $('#nt__suggest .from').html(NtLoctionArr[ranLocation]);
      showSlaesPopUp();
      $( 'body' ).on( 'click', '.suggest-close', function(e) {
          e.preventDefault();
          setTimeout(function() {
             unloadSalesPopup();
             nt_check = true;
         }, 100);
      });
    }    
   var ClassUp = NTsuggest.ClassUp; //slideInUp, fadeIn
       if ( ClassUp=='swing' || ClassUp=='shake' || ClassUp=='wobble' || ClassUp=='jello'){ClassDown ='bounceOutDown'}
       else{var ClassDown = NTsuggest.ClassUp.replace('InUp','OutDown').replace('In','Out');}//slideOutDown, fadeOut
   function showSlaesPopUp() {
     $wrap.show();
     $wrap.addClass(ClassUp);
     $wrap.removeClass(ClassDown); 
   }
   function hideSlaesPopUp() {
      $wrap.removeClass(ClassUp);
      $wrap.addClass(ClassDown); 
   }
})( jQuery );