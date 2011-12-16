Brewery = function(){
    this.init();
}
$.extend(Brewery.prototype, {
    orders: {'ingredients': {'1': 'ingredient', '2': 'type', '3': 'use', '4': 'percent', '5': 'time', '6': 'amount'},
                  'mash': {'1': 'step', '2': 'duration', '3': 'temperature'}
    },
    init: function(){
       this.set_fermentation(1);
    },
    set_style: function(style_id){
      	$.getJSON('/json/brewery/bjcp/style/'+style_id+'/', function(data) {
			$('#style_og').val(data.og_range);
			$('#style_fg').val(data.fg_range);
			$('#style_srm').val(data.srm_range);
			$('#style_ibu').val(data.ibu_range);
			$('#style_abv').val(data.abv_range);
		})
    },
    reverse_arrow: function(th_id){
        if($('#'+th_id.id+'_arrow').attr("src").match(/up/)){
            $('#'+th_id.id+'_arrow').attr("src", "/static/images/arrow_down.png")
        } else {
            $('#'+th_id.id+'_arrow').attr("src", "/static/images/arrow_up.png")
        }
    },
    toggle_select: function(list){
        $.each($('table#'+list+' tbody tr'), function(index, value){
            $('input', $(value)).prop('checked') ? $('input', $(value)).prop('checked', false) : $('input', $(value)).prop('checked', true)
        })
    },
    set_recipe: function(recipe_type){
        if(recipe_type == 0){
            $('#mash_title').hide();
            $('#mash_section').hide();
        } else {
            $('#mash_title').show();
            $('#mash_section').show();
        }
    },
    set_fermentation: function(ferm_type){
        var ferm_ids = ['label', 'data', 'time'];
        var ferm_prefix = '#stage';
        for(var i=1; i<4; i++){
            $.each(ferm_ids, function(index){
                var idset = [ferm_prefix, i, ferm_ids[index]].join('_')
                if(i <= ferm_type){
                    $(idset).show();
                } else {
                    $(idset).hide();
                }
            })
        }
    },
    append_row: function(data_grid, data_row){
        checkbox = function(id){
            var td = this.el('td', 'select'+id);
            var check = this.el('input', 'checkbox_'+id);
            check.attr('type', 'checkbox');
            td.append(check);
            return td;        
        }.bind(this);        
        var table = $('table#'+data_grid+' tbody');
        var tr_id = table.children().size();
        if(tr_id === 1 && table.find('#'+data_grid+'_blank_list')){
            table.find('#'+data_grid+'_blank_list').remove();
            --tr_id;
        }
        var tr = this.el('tr', data_grid+tr_id);
        tr.append(checkbox(tr_id));
        var data_grid_order = this.orders[data_grid];
        for(var i=1; i<=Object.keys(data_grid_order).length; i++){
            var td = this.el('td', data_grid_order[i]+tr_id);
            td.html(data_row[data_grid_order[i]]);
            tr.append(td)
        }
        table.append(tr);
    },
    remove_row: function(data_grid, row_id){
        var deleted_row = $('#'+data_grid+row_id);
        var tbody = deleted_row.parent();
        deleted_row.remove();
        if(tbody.size() === 1){
            var span = Object.keys(this.orders[data_grid]).length+1; // +1 for the checkbox column suckas
            var td = this.el('td', span);
            td.attr('colspan', span);
            td.html('This list is empty');
            var tr = this.el('tr', data_grid+'_blank_list');
            tr.append(td)
            tbody.append(tr);
        }
    },
    el: function(type, id){
        var el = $(document.createElement(type));
        el.attr('id', id);
        return el;
    }
})