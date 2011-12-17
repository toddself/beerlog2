Brewery = function(){
    this.init();
}
$.extend(Brewery.prototype, {
    orders: {'ingredients': {'1': 'ingredient', '2': 'type', '3': 'use', '4': 'percent', '5': 'time', '6': 'amount'},
             'mash': {'1': 'step', '2': 'duration', '3': 'temperature'},
             'hop_table': {'1': 'name', '2': 'alpha', '3': 'hop_form', '4': 'hop_type', '5': 'origin', '6': 'short_description'},
             'fermentable_table': {'1': 'name', '2': 'color', '3': 'potential', '4': 'max_in_batch', '5': 'must_mash'},
             'yeast_table': {'1': 'yeast_id', '2': 'lab', '3': 'name', '4': 'yeast_type', '5': 'flocc', '6': 'avg_attenuation', '7': 'max_temp'}
    },
    init: function(){
       this.set_fermentation(1);
       $.each($('#browsers').children(), function(index, value){
           $(value).hide();
       })
    },
    set_style: function(style_id){
      	$.getJSON('/brewery/bjcp/style/'+style_id+'/json/', function(data) {
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
    append_row: function(data_grid, data_row, selector_type){
        selector = function(id, widget, name){
            var td = this.el('td', 'select'+id);
            var select = this.el('input', 'selector_'+id);
            if(widget !== 'radio'){
                name = name + id;
            } else {
                select.attr('value', id);
            }
            select.attr('type', widget);
            select.attr('name', name+widget);
            td.append(select);
            return td;        
        }.bind(this);        
        var table = $('table#'+data_grid+' tbody');
        var tr_id = table.children().size();
        if(tr_id === 1 && table.find('#'+data_grid+'_blank_list')){
            table.find('#'+data_grid+'_blank_list').remove();
            --tr_id;
        }
        var tr = this.el('tr', data_grid+tr_id);
        tr.append(selector(tr_id, selector_type, data_grid));
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
    },
    show_ingredients: function(el){
        var ingredient = $(el).attr('id');
        var bframe = '#'+ingredient+'_browser';
        $.getJSON('/brewery/ingredients/'+ingredient+'/json/', function(ing){
            var data_grid = ingredient+'_table';
            this[ingredient] = {};
            $.each(ing, function(index, value){
                this[ingredient][value.name] = value;
                this.append_row(data_grid, value, 'radio');
            }.bind(this));
            var top = $(el).offset().top + $(el).height()+5;
            var left = $(el).offset().left;
            $(bframe).css('top', top);
            $(bframe).css('left', left);
            $(bframe).draggable();
            $(bframe).show();

        }.bind(this));
    },
    add_ingredient: function(ingredient){
        var data_grid = '#'+ingredient+"_table";
        var radio = data_grid+' input[type=radio]:checked';
        var row = $(radio).attr('value');
        var name = $(radio).parent().parent().find('#name'+row).html();
        console.log(b[ingredient][name])
    }
}) // 8116921 jose