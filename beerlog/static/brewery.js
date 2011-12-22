// safari you have no fucking bind?
if (Function.prototype.bind == null) {
    Function.prototype.bind = (function (slice){
        // (C) WebReflection - Mit Style License
        function bind(context) {
            var self = this; // "trapped" function reference
            if (1 < arguments.length) {
                var $arguments = slice.call(arguments, 1);
                return function () {
                    return self.apply(
                        context,
                        arguments.length ?
                            $arguments.concat(slice.call(arguments)) :
                            $arguments
                    );
                };
            }
            return function () {
                return arguments.length ? self.apply(context, arguments) : self.call(context);
            };
        }
       return bind;
    }(Array.prototype.slice));
}

function dynamicSort(property) {
    return function (a,b) {
        return (a[property] < b[property]) ? -1 : (a[property] > b[property]) ? 1 : 0;
    }
}

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
    uses: ['Mash', 'First Wort', 'Boil', 'Flameout', 'Whirlpool', 'Primary', 'Secondary', 'Bottling'],
    timing: ['min', 'minute', 'minutes', 'hrs', 'hour', 'hours', 'days', 'day', 'weeks', 'week', 'hr'],
    amounts: ['mg', 'milligram', 'milligrams', 'gm', 'grams', 'gram', 'g', 
                'oz', 'ounces', 'ounce', 'lb', 'lbs', 'pounds', 'pound', 'kg', 
                'kilos', 'kilograms', 'kilogram', 'ml', 'milliliters',
                'milliliter', 'mils', 'tsp', 'teaspoon', 'teaspoons', 'tbls', 
                'tbsp', 'tablespoon', 'tablespoons', 'cup', 'cups', 'pt',
                'pint', 'pints', 'qt', 'quart', 'quarts', 'l', 'liter',
                'liters', 'gal', 'gallon', 'gallons', 'items', 'item'],
    ingredients: [],
    mashes: [],
    init: function(){
       this.set_fermentation(1);
       $.each($('#browsers').children(), function(index, value){
           $(value).hide();
       })
       $('#yeast_starter_info').hide();
       $('#late_boil_info').hide();
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
    clear_table: function(table){
        $.each($('#'+table+' tbody tr'), function(idx, val){
            this.remove_row(table, val);
        })
        
    }, 
    populate_table: function(table){
        for(var i=1; i<=Object.keys(this[table]); i++){
            this.append_row(table, this[table][i], true, true);
        }
    },
    add_ingredient: function(ingredient){
        this.append_row('ingredients', ingredient, true, true);      
        this.add_ingredient_to_kind_list(ingredient.type.toLowerCase(), ingredient)
        this.ingredients.push(ingredient);
        this.recalculate_recipe();
    },
    delete_ingredient: function(ingredient){
        $.each($('#'+data_grid).find('tr.selected'), function(row_index, row_value){
            var row_num = this.get_selected_row_id(row_value);
            var obj = this[data_grid][row_num];
            var ingredient = obj.type.toLowerCase();
            this.ingredients.split(row_num, 1);
            remove_row('ingredients', row_num);
            this.delete_ingredient_from_kind_list(ingredient.type, ingredient)
        });
    },
    append_row: function(data_grid, data_row, multiple, checkbox){
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
        var tr = this.el('tr', data_grid+'_'+tr_id);
        tr.attr('onclick', 'b.select_row(this, '+multiple+', '+checkbox+')');
        if(checkbox === true){
            tr.append(selector(tr_id, 'checkbox', data_grid));
        }
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
        $.getJSON('/brewery/ingredients/'+ingredient+'/json/', 
        function(ing){
            var data_grid = ingredient+'_table';
            this[ingredient] = {};
            $.each(ing, function(index, value){
                this[ingredient][value.name] = value;
                this.append_row(data_grid, value, false, false);
            }.bind(this));
            var top = $(el).offset().top + $(el).height()+5;
            var left = $(el).offset().left;
            $(bframe).css('top', top);
            $(bframe).css('left', left);
            $(bframe).draggable();
            $(bframe).show();
        }.bind(this));
    },
    add_ingredient_to_kind_list: function(ingredient, obj){
        if($('#'+ingredient).val()){
            var ingredients_store = JSON.parse($('#'+ingredient).val());
        } else {
            var ingredients_store = [];
        }
        ingredients_store.push(obj);
        $('#'+ingredient).val(JSON.stringify(ingredients_store));        
    },
    delete_ingredient_from_kind_list: function(ingredient, obj){
        if($('#'+ingredient).val()){
            var ingredients_store = JSON.parse($('#'+ingredient).val());
            $.each(ingredients_store, function(idx, val){
                if((val.name === obj.name) &&
                   (val.amount === obj.amount) &&
                   (val.time === obj.time) &&
                   (val.use == obj.use)){
                       ingredients_store.splice(idx, 1);
               }
           });
        }
    },
    get_selected_row_id: function(row_identifier){
      var item_row = $(row_identifier).attr('id');
      return item_row[item_row.length-1];  
    },
    add_hop: function(){
        var item_name = $('#name'+this.get_selected_row_id('#hop_table tr.selected')).html();
        var usage = $('#hop_use').val();
        var time = $('#hop_time').val();
        var time_measure = $('#hop_time_measure').val();
        var amount = $('#hop_amount').val();
        var amount_measure = $('#hop_amount_measure').val();
        var percentage = this.calculate_percentage(ingredient, amount);
        var ing_obj = b.hop[item_name];
        ing_obj['amount'] = amount+' '+this.amounts[amount_measure];
        ing_obj['amount_measure'] = amount_measure;
        ing_obj['time'] = time+' '+this.timing[time_measure];
        ing_obj['time_measure'] = time_measure;
        ing_obj['percent'] = percentage;
        ing_obj['usage_id'] = usage;
        ing_obj['use'] = this.uses[usage];
        ing_obj['ingredient'] = item_name;
        ing_obj['type'] = "Hop";
        this.add_ingredient(ing_obj)
    },
    select_row: function(row, multiple, checkbox){        
        if($(row).attr('class') === 'selected'){
            $(row).removeClass('selected');
        } else {
            if((multiple === false) && $(row).parent().find('.selected')){
                $.each($(row).parent().find('.selected'), function(index, value){
                    $(value).removeClass('selected')
                })
            }
            $(row).addClass('selected');
            if(checkbox === true){
                $(row).find('input[type=checkbox]').click();
            }
        }
    },
    calculate_percentage: function(){
        return '100%';
    },
    recalculate_recipe: function(){
        return '';
    }
})