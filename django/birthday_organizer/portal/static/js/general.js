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


$(document).ready(function(){

    var showDownConverter = new showdown.Converter();
    showDownConverter.setOption('emoji', true);


    /*
    *
    * General setup
    *
    */

    // Change theme dynamically in the setting page
    $('select[name=theme]').bind('change', function(){
        var sel_theme = $(this).val().toLowerCase();
        $('.theme-stylesheet-' + sel_theme).attr('disabled', false);
        $('.theme-stylesheet').not($('.theme-stylesheet-' + sel_theme)).attr('disabled', 'disabled');
        $.ajax({
            type: "POST", headers: {'X-CSRFToken': getToken()},
            url: 'change_theme',
            data: {'theme': $(this).val()},
            success: function(data){
                // Nothing to do
            },
            error: function(data){
                console.error('Unable to change the theme dynamically.')
            }
        });
    })

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
    function setToolTip(){
        $('.tooltip-trigger').tooltip();
    }

    // Convert dates to localtime
    function convertDates(){
        $('.convert-date').each(function(i, e){
            var date = new Date($(e).text() + ' UTC');
            $(e).text(date.toLocaleDateString('en-GB', {
                day : 'numeric',
                month : 'short',
                year : 'numeric',
                hour: 'numeric',
                minute: 'numeric',
                second: 'numeric'
            }));
        })
    }

    //Bind confirm events
    $('.confirm').each(function(i, e){
        $(e).click(function(event){
            $("<div>").html("Are you sure you want to delete this?").dialog({
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

    /*
    *
    * Payment events
    *
    */

    // Update total payment on add/remove payment
    function refresh_total_payments(event){
        $.ajax({
            type: "POST", headers: {'X-CSRFToken': getToken()},
            url: 'get_total',
            data: {'event': event},
            success: function(data){
                if (data['result'] == 'success'){
                    var total = data['content'].toFixed(2);
                    $('.total-money').html(total);
                }
                else {
                    console.error(data['details']);
                }
            },
            error: function(data){
                console.error('Unable to refresh the payment totals.')
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
                    setUpPayments();
                    refresh_total_payments(event);
                }
                else {
                    console.error(data['details']);
                }
            },
            error: function(data){
                console.error('Unable to add a new payment.')
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
                else {
                    console.error(data['details']);
                }
            },
            error: function(data){
                console.error('Unable to toggle confirmation for payment.')
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
                    setUpPayments();
                    refresh_total_payments(event);
                }
                else {
                    console.error(data['details']);
                }
            },
            error: function(data){
                console.error('Unable to remove payment.')
            }
        });
    }

    // Bind toggle events (on load and on JSON content update)
    function bindPaymentToggleEvents(){
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


    /*
    *
    * Comment events
    *
    */

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
                    setUpComments();
                }
                else {
                    console.error(data['details']);
                }
            },
            error: function(data){
                console.error('Unable to make new comment.')
            }
        });
    })

    // Bind edit comment events
    function bindEditComments(){
        $('.edit-comment-button').click(function(){
            $(this).parents('fieldset').find('.showdown-trigger').remove();
            $(this).parents('fieldset').find('.edit-comment-submit').removeClass('hidden');
            $(this).parents('fieldset').find('.edit-comment-area').removeClass('hidden');
            $(this).parents('fieldset').find('.edit-comment-button').remove();
        });
        $('.edit-comment-submit').bind('click', function(){
            var input = $(this).parents('fieldset').find('.edit-comment-area');
            var content = input.val();
            var event = input.data('event');
            var comment = input.data('comment');
            $.ajax({
                type: "POST", headers: {'X-CSRFToken': getToken()},
                url: 'edit_comment',
                data: {'comment': comment, 'event': event, 'content': content},
                success: function(data){
                    if (data['result'] == 'success'){
                        $('.events-list').children().remove();
                        content = jQuery.parseHTML(data['content']);
                        $('.events-list').append(content);
                        setUpComments();
                    }
                    else {
                        console.error(data['details']);
                    }
                },
                error: function(data){
                    console.error('Unable to edit comment.')
                }
            });
        });
    }

    // Change like status of a comment
    function toggleLike(el, status){
        var event = el.data('event');
        var comment = el.data('comment');
        $.ajax({
            type: "POST", headers: {'X-CSRFToken': getToken()},
            url: 'toggle_like',
            data: {'comment': comment, 'event': event, 'status': status},
            success: function(data){
                if (data['result'] == 'success'){
                    $('.events-list').children().remove();
                    content = jQuery.parseHTML(data['content']);
                    $('.events-list').append(content);
                    setUpComments();
                }
                else {
                    console.error(data['details']);
                }
            },
            error: function(data){
                console.error('Unable to toggle like.')
            }
        });
    }

    // Bind toggle like events
    function bindToggleLike(){
        $('.like-button').click(function(){
            $(this).parents('fieldset').find('.like-button').addClass('hidden');
            $(this).parents('fieldset').find('.dislike-button').removeClass('hidden');
            toggleLike($(this), 1)
        });
        $('.dislike-button').click(function(){
            $(this).parents('fieldset').find('.like-button').removeClass('hidden');
            $(this).parents('fieldset').find('.dislike-button').addClass('hidden');
            toggleLike($(this), 0)
        });
    }

    function applyShowdown(){
        $('.showdown-trigger').each(function(){
            $(this).html(showDownConverter.makeHtml($(this).html()));
        })
    }



    /*
    *
    * Global setup methods that are also executed when the DOM is updated after a AJAX response
    *
    */

    function setUpComments(){
        setToolTip();
        convertDates();
        applyShowdown();
        bindEditComments();
        bindToggleLike();
    }
    setUpComments();
    
    function setUpPayments(){
        setToolTip();
        bindPaymentToggleEvents();
    }
    setUpPayments();

    /*
    *
    * Filters
    *
    */

    $('#user_filter').bind('change keyup paste', function(){
        var input_val = $(this).val().toLowerCase();
        $('.user-block').each(function(i, e){
            var name = $(e).find('.user-block-name').text().toLowerCase();
            if (name.includes(input_val)) {
                $(e).show();
            }
            else{
                $(e).hide();
            }
        })
    })

});
