$(document).ready(function(){
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", CSRF_TOKEN);
            }
        }
    });

    var table_sr = $('#tbl_sr_modal').DataTable({
        "pageLength": 8
    });

    var table_sr_line = $('#tbl_sr_line_modal').DataTable({
        "pageLength": 8,
        "bInfo" : false,
        "bPaginate": false,
        "bFilter": false,
        "paging": false,
        "bSort": false
    });

    $("#tbl_sr_modal").on('click','tr',function(){
        $(this).addClass('selected').siblings().removeClass('selected');    
     });

    $("#tbl_sr_line_modal").on('click','tr',function(){
        $(this).addClass('selected').siblings().removeClass('selected');
        $("#item_name").val($("#tbl_sr_line_modal tr.selected td:nth-child(3)").html());
        $("#unit").val($("#tbl_sr_line_modal tr.selected td:nth-child(6)").html());
        $("#lot_no").val($("#tbl_sr_line_modal tr.selected td:nth-child(4)").html());
        $("#expiry").val($("#tbl_sr_line_modal tr.selected td:nth-child(5)").html());
        $("#quantity").val($("#tbl_sr_line_modal tr.selected td:nth-child(7)").html());
        if (!($("#item_name").val() == '')){
            $('#btn_add_sr_line').prop('disabled', false);
        }

        var fast_slow = $("#tbl_sr_line_modal tr.selected td:nth-child(9)").find('div').html();
        var warehouse = $("#warehouse").val();

        $.ajax({
            url: '/iwms/api/bin-locations?fast_slow=' + fast_slow + '&warehouse=' + warehouse,
            type: 'GET',
            contentType: "application/json; charset=utf-8",
            success: function(data){
                if(data.bins.length>0){
                    $("#bin_location").empty();
                    var option = $('<option></option>').attr("value", "").text("Choose...");
                    $("#bin_location").append(option);
                    var i = 0;
                    for (i; i < data.bins.length; ++i){
                        var option = $('<option></option>').attr("value", data.bins[i].id).text(data.bins[i].code);
                        $("#bin_location").append(option);
                    }
                }
            }
        });
    });

    $("#btn_add_sr_line").click(function(){
        $("#p_item_name").html("<strong>ITEM NAME: </strong>" + $("#item_name").val());
        $("#p_qty").html("<strong>RECEIVED QUANTITY: </strong>" + $("#quantity").val());
        $("#p_lot_no").html("<strong>LOT NUMBER: </strong>" + $("#lot_no").val());
        $("#p_expiry_date").html("<strong>EXPIRY DATE: </strong>" + $("#expiry").val());
    });

    $("#btn_confirm_sr_line").click(function(){
        var stock_id = $("#tbl_sr_line_modal tr.selected td:first").html();
        var item_no = $("#tbl_sr_line_modal tr.selected td:nth-child(2)").html();
        var item_name = $("#tbl_sr_line_modal tr.selected td:nth-child(3)").html();
        var base_uom = $("#tbl_sr_line_modal tr.selected td:nth-child(6)").html();
        var lot_no = $("#lot_no").val();
        var expiry_date = $("#expiry").val();
        var bin_location = $.trim(($("#bin_location option:selected").text()));
        var quantity = $("#quantity").val();
        var timestamp = + new Date();

            var row = $("#tbl_sr_line_modal tr.selected");
            $('#tbl_pwy_item_line tr:last').after(
                `<tr>
                    <td style="display:none;"><input name="pwy_items[]" type="hidden" value="${stock_id}"></input></td>
                    <td></td>
                    <td class='text-center'>${item_no}</td>
                    <td class='text-center'>${item_name}</td>
                    <td class='text-center'><input name="uom_${stock_id}" type="text" value="${base_uom}" style="width:50px" readonly></td>
                    <td class='text-center'><input name="bin_location_${stock_id}" type="text" value="${bin_location}" style="width:50px" readonly></td>
                    <td class='text-center'><input name="lot_no_${stock_id}" type="text" value="${lot_no}" style="width:50px" readonly></td>
                    <td class='text-center'><input name="expiry_${stock_id}" type="text" value="${expiry_date}" style="width:80px" readonly></td>
                    <td class='text-center'><input name="qty_${stock_id}" type="text" value="${quantity}" style="width:50px" readonly></td>
                    <td class='text-center'><input name="timestamp_${stock_id}" type="text" value="${timestamp}" style="width:110px" readonly></td>
                </tr>
                `
                );

            // ADDING NEW QUANTITY TO THE PREV STORED
            var prev_stored = $("#tbl_sr_line_modal tr.selected td:nth-child(8)");
            var _add = parseInt(prev_stored.html()) + parseInt(quantity);
            prev_stored.html(_add);
            
            // MAKING ROW COLOR GREEN
            row.removeClass('list-group-item-danger')
            row.addClass('list-group-item-success');

            // CLEANING INPUTS
            $('#btn_add_sr_line').prop('disabled', true);
            $("#p_item_name").html("");
            $("#p_qty").html("");
            $("#p_lot_no").html("");
            $("#p_expiry_date").html("");
            $("#item_name").val("");
            $("#bin_location").val("");
            $("#unit").val("");
            $("#quantity").val("");
            $("#expiry").val("");
    });

    $('#btn_select_sr').click(function(){
        // Clearing SR line and PO line table
        table_sr_line.clear().draw();
        $("#tbl_pwy_item_line tr").each(function() {
            if ($(this).find("input").eq(0).val()){
                $(this).remove();
            }
        });

        var number = $("#tbl_sr_modal tr.selected td:nth-child(2)").html();
        var sr_id = $("#tbl_sr_modal tr.selected td:first").html();
        var reference = $("#tbl_sr_modal tr.selected td:nth-child(4)").html();
        var warehouse = $("#tbl_sr_modal tr.selected td:nth-child(5)").html();
        var remarks = $("#tbl_sr_modal tr.selected td:nth-child(6)").html();

        $("#sr_number").val(number);
        $("#reference").val(reference);
        $("#warehouse").val(warehouse);
        $("#remarks").val(remarks);
        
        $.ajax({
            url: '/iwms/api/stock-receipts/' + sr_id + '/products',
            type: 'GET',
            contentType: "application/json; charset=utf-8",
            success: function(data){
                for (i=0; i < data.items.length; ++i){
                    var fast_slow = "";
                    if(data.items[i].fast_slow == 'FAST'){
                        fast_slow = '<div class="mb-2 mr-2 badge badge-success">FAST</div>';
                    }else if(data.items[i].fast_slow == 'SLOW'){
                        fast_slow = '<div class="mb-2 mr-2 badge badge-danger">SLOW</div>'
                    }else{
                        fast_slow = '<div></div>'
                    }
                    var row = table_sr_line.row.add([
                    data.items[i].id,
                    data.items[i].number,
                    data.items[i].name,
                    data.items[i].lot_no,
                    data.items[i].expiry_date,
                    data.items[i].uom,
                    data.items[i].received_qty,
                    data.items[i].prev_stored,
                    fast_slow
                    ]);
                    table_sr_line.row(row).column(0).nodes().to$().addClass('myHiddenColumn');
                    if (data.items[i].is_putaway){
                        table_sr_line.row(row).nodes().to$().addClass('list-group-item-success');
                    }else{
                        table_sr_line.row(row).nodes().to$().addClass('list-group-item-danger');
                    }
                    table_sr_line.row(row).draw();
                }
            }
        });
    });
     
});

(function() {
    var fixed_footer = document.getElementById('chkbox_fixed_footer');
    setTimeout(function() {
      fixed_footer.click();
    }, 100);
  })();