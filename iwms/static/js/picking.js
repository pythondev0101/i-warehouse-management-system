$(document).ready(function(){

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", CSRF_TOKEN);
            }
        }
    });

    var table_sr = $('#tbl_so_modal').DataTable({
        "pageLength": 8
    });

    var table_so_line = $('#tbl_so_line_modal').DataTable({
        "order": [[1,'asc']]
    });

    $("#tbl_so_modal").on('click','tr',function(){
        $(this).addClass('selected').siblings().removeClass('selected');    
    });


    $("#tbl_so_line_modal").on('click','tr',function(){
        $(this).addClass('selected').siblings().removeClass('selected');
        $("#item_name").val($("#tbl_so_line_modal tr.selected td:nth-child(3)").html());
        $("#unit").val($("#tbl_so_line_modal tr.selected td:nth-child(5)").html());
        $("#lot_no").val($("#tbl_so_line_modal tr.selected td:nth-child(6)").html());
        $("#expiry").val($("#tbl_so_line_modal tr.selected td:nth-child(7)").html());
        $("#bin_location").val($("#tbl_so_line_modal tr.selected td:nth-child(4)").html());
        if (!($("#item_name").val() == '')){
            $('#btn_add_so_line').prop('disabled', false);
        }  
        
        var _unit_qty = $("#tbl_so_line_modal tr.selected td:nth-child(8)").html();
        $("#quantity").attr('max',_unit_qty);
    });


    $("#btn_add_so_line").click(function(){
        $("#p_item_name").html("<strong>ITEM NAME: </strong>" + $("#item_name").val());
        $("#p_qty").html("<strong>PICK QUANTITY: </strong>" + $("#quantity").val());
        $("#p_bin_location").html("<strong>LOCATION: </strong>" + $("#bin_location").val());
        $("#p_lot_no").html("<strong>LOT NUMBER: </strong>" + $("#lot_no").val());
        $("#p_expiry_date").html("<strong>EXPIRY DATE: </strong>" + $("#expiry").val());
    });


    $('#btn_select_so').click(function(){
        // Clearing SR line and PO line table

        table_so_line.clear().draw();
        $("#tbl_so_line tr").each(function() {
            if ($(this).find("input").eq(0).val()){
                $(this).remove();
            }
        });

        var so = $("#tbl_so_modal tr.selected td:nth-child(2)").html();
        var so_id = $("#tbl_so_modal tr.selected td:nth-child(1)").html();
        var remarks = $("#tbl_so_modal tr.selected td:nth-child(4)").html();
        $("#so_number").val(so);
        $("#remarks").val(remarks);

        $.ajax({
            url: '/iwms/api/sales-orders/' + so_id + "/products",
            type: 'GET',
            contentType: "application/json; charset=utf-8",
            success: function(data){
                for (i=0; i < data.items.length; ++i){
                    var row = table_so_line.row.add([
                    data.items[i].id,
                    data.items[i].number,
                    data.items[i].name,
                    data.items[i].bin_location,
                    data.items[i].uom,
                    data.items[i].lot_no,
                    data.items[i].expiry_date,
                    data.items[i].qty,data.items[i].issued_qty,
                    ]);
                    table_so_line.row(row).column(0).nodes().to$().addClass('myHiddenColumn');
                    if (data.items[i].qty == 0){
                        table_so_line.row(row).nodes().to$().addClass('list-group-item-success');
                    }else if(data.items[i].issued_qty == 0){
                        table_so_line.row(row).nodes().to$().addClass('list-group-item-danger');
                    }else{
                        table_so_line.row(row).nodes().to$().addClass('list-group-item-warning');
                    }
                    table_so_line.row(row).draw();
                }
            }
        });
    });
    

    $("#btn_confirm_so_line").click(function(){
        var stock_id = $("#tbl_so_line_modal tr.selected td:first").html();
        var item_no = $("#tbl_so_line_modal tr.selected td:nth-child(2)").html();
        var item_name = $("#tbl_so_line_modal tr.selected td:nth-child(3)").html();
        var base_uom = $("#tbl_so_line_modal tr.selected td:nth-child(6)").html();
        var lot_no = $("#lot_no").val();
        var expiry_date = $("#expiry").val();
        var bin_location = $("#bin_location").val();
        var quantity = $("#quantity").val();
        var timestamp = + new Date();
        var picker = "";

            var row = $("#tbl_so_line_modal tr.selected");
            $('#tbl_pwy_item_line tr:last').after(
                `<tr>
                    <td style="display:none;"><input name="pick_items[]" type="hidden" value="${stock_id}"></input></td>
                    <td></td>
                    <td class='text-center'>${item_no}</td>
                    <td class='text-center'>${item_name}</td>
                    <td class='text-center'><input name="bin_location_${stock_id}" type="text" value="${bin_location}" style="width:50px" readonly></td>
                    <td class='text-center'><input name="lot_no_${stock_id}" type="text" value="${lot_no}" style="width:50px" readonly></td>
                    <td class='text-center'><input name="expiry_${stock_id}" type="text" value="${expiry_date}" style="width:80px" readonly></td>
                    <td class='text-center'><input name="uom_${stock_id}" type="text" value="${base_uom}" style="width:50px" readonly></td>
                    <td class='text-center'><input name="qty_${stock_id}" type="text" value="${quantity}" style="width:50px" readonly></td>
                    <td class='text-center'><input name="timestamp_${stock_id}" type="text" value="${timestamp}" style="width:110px" readonly></td>
                    <td class='text-center'>${picker}</td>
                </tr>
                `
                );

            // ADDING NEW QUANTITY TO THE QTY PICKED 
            var qty_picked = $("#tbl_so_line_modal tr.selected td:nth-child(9)");
            var _picked_item = parseInt(qty_picked.html()) + parseInt($("#quantity").val());
            qty_picked.html(_picked_item);
            
            // MAKING ROW COLOR AND REDUCING QTY
            var qty = $("#tbl_so_line_modal tr.selected td:nth-child(8)");
            var _qty_item = parseInt(qty.html()) - parseInt($("#quantity").val());
            qty.html(_qty_item);
            var issued_qty = $("#tbl_so_line_modal tr.selected td:nth-child(9)");

            if (parseInt(qty.html()) == 0){
                row.removeClass('list-group-item-danger')
                row.removeClass('list-group-item-warning')
                row.addClass('list-group-item-success');
            }else{
                row.removeClass('list-group-item-danger')
                row.addClass('list-group-item-warning');
            }

            // CLEANING INPUTS
            $('#btn_add_sr_line').prop('disabled', true);
            $("#p_item_name").html("");
            $("#p_qty").html("");
            $("#p_lot_no").html("");
            $("#p_expiry_date").html("");
            $("#item_name").val("");
            $("#bin_location").val("");
            $("#unit").val("");
            $("#quantity").val("0");
            $("#expiry").val("");
            $("#lot_no").val("");
    });

   
});

(function() {
    var fixed_footer = document.getElementById('chkbox_fixed_footer');
    setTimeout(function() {
      fixed_footer.click();
    }, 100);
  })();