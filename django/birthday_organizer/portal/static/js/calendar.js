class Calendar {

    constructor(container) {
        this.container = container;
        this.week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        this.months = ['January', 'February', 'March', 'April',
                       'May', 'June', 'July', 'August',
                       'September', 'October', 'November', 'December'];
        this.max_number_of_weeks = 6;
        this.anim_duration = 300;
        this.build_main();
        this.build_title();
        this.build_headers();
        this.build_weeks();
        this.build_buttons();
        this.build_legend();
        this.build_popup();
        this.init_days();
    }

    build_main() {
        this.table = $('<table>');
        this.container.append(this.table);
    }

    build_title() {
        var title_row = $('<tr>').addClass('calendar-title-row');
        this.title = $('<td>').attr('colspan', this.week_days.length);
        title_row.append(this.title);
        this.table.append(title_row);
    }

    build_buttons() {
        var self = this;
        var buttons_row = $('<tr>');
        var buttons_cell = $('<td>').attr('colspan', this.week_days.length);
        var back_button_text = $('<i>').addClass('fa fa-circle-left');
        var next_button_text = $('<i>').addClass('fa fa-circle-right');
        this.back_button = $('<button>').addClass('calendar-button-left');
        this.back_button.append(back_button_text).bind('click', function(){
            var month = self.month - 1;
            var year = self.year;
            if (month < 0){
                month = self.months.length - 1;
                year--;
            }
            self.update_days(year, month);
        });
        this.next_button = $('<button>').addClass('calendar-button-right');
        this.next_button.append(next_button_text).bind('click', function(){
            var month = self.month + 1;
            var year = self.year;
            if (month > self.months.length - 1){
                month = 0;
                year++;
            }
            self.update_days(year, month);
        });
        buttons_cell.append(this.back_button);
        buttons_cell.append(this.next_button);
        buttons_row.append(buttons_cell);
        this.table.append(buttons_row);
    }

    build_legend() {
        var dot = $("<div>").attr('class', 'dot');
        var legend_participating = $("<div>").text('Participating').attr('class', 'legend-participating');
        var legend_hosting = $("<div>").text('Hosting').attr('class', 'legend-hosting');
        var legend = $("<div>").attr('class', 'legend-wrapper');
        legend_participating.prepend(dot.clone());
        legend_hosting.prepend(dot.clone());
        legend.append(legend_participating);
        legend.append(legend_hosting);
        this.table.find('td').last().append(legend);
    }

    build_headers() {
        var headerRow = $('<tr>');
        this.table.append(headerRow);
        for (var i=0; i<this.week_days.length; i++){
            var header = $('<td>').text(this.week_days[i]);
            header.addClass('calendar-day-header');
            headerRow.append(header);
        }
    }

    build_weeks() {
        var self = this;
        this.weeks = [];
        for (var i=0; i<this.max_number_of_weeks; i++){
            var week = $('<tr>');
            this.table.append(week);
            this.weeks.push(week);
            for (var j=0; j<this.week_days.length; j++){
                var day = $('<td>').addClass('calendar-day');
                day.bind('click', function(event){
                    if ($(this).hasClass('empty')){
                        return;
                    }
                    self.show_events(event.target);
                })
                week.append(day);
            }
        }
    }

    build_popup() {
        var self = this;
        // Create elements
        this.popup = $('<div>').addClass('calendar-popup');
        this.popup_title = $('<div>').addClass('calendar-popup-title');
        this.popup_content = $('<div>').addClass('calendar-popup-content');
        var popup_close = $('<div>').addClass('calendar-popup-close');
        var popup_relative = $('<div>').addClass('calendar-popup-relative');
        var close_icon = $("<i>").addClass('fa fa-window-close');
        // Append elements
        this.container.append(this.popup);
        this.popup.append(popup_relative);
        popup_relative.append(this.popup_title);
        popup_relative.append(this.popup_content);
        popup_relative.append(popup_close);
        popup_close.append(close_icon);
        // Bind close events
        popup_close.bind('click', function(){
            self.close_popup()
        })
        $(document).on('keyup', function(e) {
            if (e.key == "Escape") self.close_popup()
        });
    }

    close_popup() {
        this.popup.hide('scale', this.anim_duration);
    }

    init_days() {
        var now = new Date();
        this.update_days(now.getFullYear(), now.getMonth());
    }

    update_title() {
        this.title.text(this.months[this.month] + " " + this.year);
    }

    update_days(year, month) {
        this.month = month;
        this.year = year;
        this.update_title();

        var first_date = new Date(year, month, 1);
        var last_day = new Date(year, month + 1, 0).getDate();
        var today = new Date();
        today.setHours(0, 0, 0, 0);
        // Get index of week day, normalizing so that Mon=0
        var first_date_week_index = first_date.getDay() - 1;
        if (first_date_week_index === -1){
            first_date_week_index = 6;
        }

        var temp_day = 1;
        for (var week_num=0; week_num<this.max_number_of_weeks; week_num++){
            for (var day_num=0; day_num<this.week_days.length; day_num++){
                var day = this.weeks[week_num].children().eq(day_num);
                // Empty days before first day of the month
                if (week_num === 0 && day_num < first_date_week_index){
                    day.text('').addClass('empty');
                }
                else{
                    // Normal days
                    if (temp_day <= last_day){
                        day.text(temp_day).removeClass('empty');
                        this.set_events(day);
                        // Highligh if this is today
                        var day_obj = new Date(this.year, this.month, temp_day);
                        if (day_obj.toDateString() == today.toDateString()){
                            day.addClass('today');
                        }
                        else{
                            day.removeClass('today');
                        }
                        temp_day++;
                    }
                    // Empty days after the end of the month
                    else{
                        day.text('').addClass('empty');
                    }
                }
            }
        }

    }

    set_events(container) {
        var self = this;
        $('.event-data').each(function(i, e){
            if ($(e).data('year') == self.year &&
                $(e).data('month') == (self.month + 1) &&
                $(e).data('day') == $(container).text()) {
                    var event_marker = $("<div>").attr({
                        'class': 'event-marker event-' + $(e).data('type')
                    }).data('id', $(e).data('id'));
                    container.append(event_marker);
                }
        });
    }

    prepare_popup_content(el) {
        var self = this;
        // Adjust title
        this.popup_title.text($(el).text() + ' ' + this.title.text());
        this.popup_content.children().remove();
        // Adjust content
        if (!$(el).find('.event-marker').length){
            this.popup_content.append($('<span>').text('No events'));
            return
        }
        function add_events_to_popup(i, e){
            var event_id = $(e).data('id');
            var event_data = $('#event-data-' + event_id);
            console.log();
            var event = $('<span>').text(event_data.text())
            var link = $('<a>').attr({
                'href': 'event?id=' + event_id,
                'class': 'disable-link-color calendar-event-link'
            });
            var icon = $('<i>').addClass('fa fa-external-link');
            link.append(icon);
            link.append(event);
            self.popup_content.append(link);
        }
        if ($(el).find('.event-marker.event-hosting').length){
            var header = $('<div>').text('Hosting').addClass('event-legend');
            self.popup_content.append(header);
            $(el).find('.event-marker.event-hosting').each(add_events_to_popup);
        }
        if ($(el).find('.event-marker.event-participating').length){
            var header = $('<div>').text('Participating').addClass('event-legend');
            self.popup_content.append(header);
            $(el).find('.event-marker.event-participating').each(add_events_to_popup);
        }
    }


    show_events(el) {
        // Get day-button's coordinates
        var left = $(el).offset().left - $(this.container).offset().left;
        var top = $(el).offset().top - $(this.container).offset().top;
        // Adjust to center the origin on the button's center
        left += $(el).outerWidth() / 2
        top += $(el).outerHeight() / 2
        // Prepare the content and show the popup
        this.prepare_popup_content(el);
        $('.calendar-popup').show({'effect': 'scale',
                                   'origin': [top, left],
                                   'duration': self.anim_duration})
    }

}
