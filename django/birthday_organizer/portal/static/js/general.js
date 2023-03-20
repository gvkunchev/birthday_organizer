$(document).ready(function(){

    // Handle mobile view toggle
    $('.expand-icon').click(function(){
        $('#nav-menu').toggleClass('mobile-view');
    })

    // Init a calendar if the DOM expects it
    calendar = new Calendar($('#calendar'));

    // Set click-to-copy
    $('.clipboard-data').bind('click', function(){
        var input = $(this).find('.clipboard-data-input');
        $(input).removeClass('hidden');
        if (navigator.userAgent.match(/ipad|ipod|iphone/i)) {
          input.contenteditable = true;
          input.readonly = false;
          var range = document.createRange();
          range.selectNodeContents(input);
          var selection = window.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);
          input.setSelectionRange(0, 999999);
        } else {
          input.select()
        }
        document.execCommand('copy');
        $(input).addClass('hidden');
    });

    // Engage tooltips
    $('.tooltip-trigger').tooltip();

    // Update total payment on add/remove payment
    function refresh_total_payments(event){
        $.ajax({
            type: "POST", headers: {'X-CSRFToken': getToken()},
            url: 'get_total',
            data: {'event': event},
            success: function(data){
                console.log(data);
                if (data['result'] == 'success'){
                    var total = data['content'].toFixed(2);
                    $('.total-money').html(total);
                }
            }
        });
    }

    // Add payment
    $('.add-payment-button').bind('click', function(){
        var input = $('.add-payment-amount');
        var amount = input.val();
        var event = input.data('event');
        var user = input.data('user');
        $.ajax({
            type: "POST", headers: {'X-CSRFToken': getToken()},
            url: 'add_payment',
            data: {'event': event, 'amount': amount, 'user': user},
            success: function(data){
                if (data['result'] == 'success'){
                    $('.event-participant-list-item').remove();
                    content = jQuery.parseHTML(data['content']);
                    $('.event-participant-list').append(content);
                    bindToggleEvents();
                    refresh_total_payments(event);
                }
            }
        });
    })

    // Toggle payment
    function toggleConfirmation(el, status){
        $.ajax({
            type: "POST", headers: {'X-CSRFToken': getToken()},
            url: 'toggle_payment',
            data: {'payment': el.data('payment'), 'status': status},
            success: function(data){
                if (data['result'] == 'success'){
                    $(el).parents('td').find('.payment-approved-icon').each(function(i, e){
                        $(e).toggleClass('hidden');
                    })
                }
            }
        });
    }

    // Remove payment function
    function removePayment(el){
        var input = $('.add-payment-amount');
        var event = input.data('event');
        $.ajax({
            type: "POST", headers: {'X-CSRFToken': getToken()},
            url: 'remove_payment',
            data: {'payment': el.data('payment')},
            success: function(data){
                if (data['result'] == 'success'){
                    $('.event-participant-list-item').remove();
                    content = jQuery.parseHTML(data['content']);
                    $('.event-participant-list').append(content);
                    bindToggleEvents();
                    refresh_total_payments(event);
                }
            }
        });
    }

    // Bind toggle events (on load and on JSON content update)
    function bindToggleEvents(){
        $('.payment-confirmation-trigger-true').click(function(){
            toggleConfirmation($(this), 0);
        })
        $('.payment-confirmation-trigger-false').click(function(){
            toggleConfirmation($(this), 1);
        })
        $('.payment-remove-trigger').bind('click', function(){
            removePayment($(this));
        })
    }
    bindToggleEvents();

    // Add comment
    $('#make_comment').bind('click', function(){
        var input = $('#comment');
        var content = input.val();
        var event = input.data('event');
        var user = input.data('user');
        $.ajax({
            type: "POST", headers: {'X-CSRFToken': getToken()},
            url: 'add_comment',
            data: {'event': event, 'content': content, 'user': user},
            success: function(data){
                if (data['result'] == 'success'){
                    $('.events-list').children().remove();
                    content = jQuery.parseHTML(data['content']);
                    $('.events-list').append(content);
                    input.val('');
                }
            }
        });
    })

    //Bind confirm events
    $('.confirm').each(function(i, e){
        $(e).click(function(event){
            $("<div>").html("Are you sure you want to delete this event?").dialog({
                title: "Please confirm",
                buttons: [
                  {
                    text: "OK",
                    click: function() {
                        window.location.href = $(e).attr('href');
                        $(this).dialog("close");
                    }
                  },
                  {
                    text: "Cancel",
                    click: function() {
                        $(this).dialog("close");
                    }
                  }
                ]
              });
            event.preventDefault();
        })
    })
});

// Get csrftoken from cookies
function getToken() {
    let name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
