$(document).ready(function(){
    
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", CSRF_TOKEN);
            }
        }
    });

    var table_po = $('#tbl_po_modal').DataTable({
        "pageLength": 8
    });

    var table_po_line = $('#tbl_po_line_modal').DataTable({
        "pageLength": 8,
        "bInfo" : false,
        "bPaginate": false,
        "bFilter": false,
        "paging": false,
        "bSort": false,
    });

    $("#tbl_po_modal").on('click','tr', function(){
        $(this).addClass('selected').siblings().removeClass('selected');    
     });

     
    $("#tbl_po_line_modal").on('click','tr',function(){
        $(this).addClass('selected').siblings().removeClass('selected');
        $("#item_name").val($("#tbl_po_line_modal tr.selected td:nth-child(3)").html());
        $("#unit").val($("#tbl_po_line_modal tr.selected td:nth-child(4)").html());
        if (!($("#item_name").val() == '')){
            $('#btn_add_po_line').prop('disabled', false);
        }
    });


    $("#btn_add_po_line").click(function(){
        $("#p_item_name").html("<strong>ITEM NAME: </strong>" + $("#item_name").val());
        $("#p_qty").html("<strong>RECEIVED QUANTITY: </strong>" + $("#quantity").val());
        $("#p_lot_no").html("<strong>LOT NUMBER: </strong>" + $("#lot_no").val());
        $("#p_expiry_date").html("<strong>EXPIRY DATE: </strong>" + $("#expiry_date").val());

    });


    $("#btn_confirm_po_line").click(function(){
        var stock_id = $("#tbl_po_line_modal tr.selected td:first").html();
        var item_no = $("#tbl_po_line_modal tr.selected td:nth-child(2)").html();
        var item_name = $("#tbl_po_line_modal tr.selected td:nth-child(3)").html();
        var base_uom = $("#tbl_po_line_modal tr.selected td:nth-child(4)").html();
        var e_qty = $("#quantity").val();
        var lot_no = $("#lot_no").val();
        var expiry_date = $("#expiry_date").val();
        var net_weight = $("#net_weight").val();
        var row = $("#tbl_po_line_modal tr.selected");
        var timestamp = + new Date();
            $('#tbl_sr_line tr:last').after(
                `<tr>
                    <td style="display:none;"><input name="sr_items[]" type="hidden" value="${stock_id}"></input></td>
                    <td></td>
                    <td class='text-center'>${item_no}</td>
                    <td class='text-center'>${item_name}</td>
                    <td class='text-center'><input name="lot_no_${stock_id}" type="text" value="${lot_no}" readonly></td>
                    <td class='text-center'><input name="expiry_date_${stock_id}" type="text" value="${expiry_date}" style="width:80px" readonly></td>
                    <td class='text-center'><input name="uom_${stock_id}" type="text" value="${base_uom}" style="width:50px" readonly></td>
                    <td class='text-center'><input name="received_qty_${stock_id}" type="number" value="${e_qty}" style="width:50px" readonly></td>
                    <td class='text-center'><input name="net_weight_${stock_id}" type="text" value="${net_weight}" style="width:50px" readonly></td>
                    <td class='text-center'><input name="timestamp_${stock_id}" type="text" value="${timestamp}" style="width:110px" readonly></td>
                </tr>
                `
                );
            // UPDATING RECEIVED QTY, REMAINING QTY = EXCEPTED - RECEIVED QTY
            var received_qty = $("#tbl_po_line_modal tr.selected td:nth-child(6)");
            if (received_qty.html() == ''){
                received_qty.html(e_qty);
            }else{
                received_qty.html(parseInt(received_qty.html()) + parseInt(e_qty));
            }
            var remaining_qty = $("#tbl_po_line_modal tr.selected td:nth-child(7)");
            remaining_qty.html(parseInt(remaining_qty.html()) - parseInt(e_qty));
            
            // ADDING ROW COLOR,GREEN MEANS NO REMAINING QTY
            // RED MEANS NOT ADDED
            // YELLOW MEANS HAS REMAINING QTY

            if (parseInt(remaining_qty.html()) == 0){
                row.removeClass('list-group-item-danger')
                row.removeClass('list-group-item-warning')
                row.addClass('list-group-item-success');
            }else{
                row.removeClass('list-group-item-danger')
                row.addClass('list-group-item-warning');
            }

            // CLEARING FIELDS
            $('#btn_add_po_line').prop('disabled', true);
            $("#p_item_name").html("");
            $("#p_qty").html("");
            $("#p_lot_no").html("");
            $("#p_expiry_date").html("");
            $("#item_name").val("");
            $("#quantity").val("0");
            $("#unit").val("");
            $("#lot_no").val("");
            $("#net_weight").val("");
            $("#expiry_date").val("{{form.date_received.data.strftime('%Y-%m-%d')}}");
            
            var sr_number = "{{sr_generated_number}}";
            var po_number = $("#po_number").val();
            var supplier = $("#supplier").val();

            var label = prompt("How many label?", "1");
            if (!(label == null)){
              
                $.ajax({
                    url: '/iwms/_create_label',
                    type: 'POST',
                    dataType: 'json',
                    data: JSON.stringify({
                        'label':label,'lot_no':lot_no,'expiry_date':expiry_date,
                        'quantity': e_qty, 'sr_number': sr_number, 'po_number': po_number,
                        'stock_id': stock_id,'supplier':supplier
                    }),
                    contentType: "application/json; charset=utf-8",
                    success: function(data){
                    }
                });
            }
    });


    $('#btn_select_po').click(function(){
        // Clearing SR line and PO line table
        table_po_line.clear().draw();
        $("#tbl_sr_line tr").each(function() {
            if ($(this).find("input").eq(0).val()){
                $(this).remove();
            }
        });

        var number = $("#tbl_po_modal tr.selected td:nth-child(2)").html();
        var supplier = $("#tbl_po_modal tr.selected td:nth-child(3)").html();
        var warehouse = $("#tbl_po_modal tr.selected td:nth-child(4)").html();
        var po_id = $("#tbl_po_modal tr.selected td:first").html();
        var remarks = $("#tbl_po_modal tr.selected td:nth-child(5)").html();
        $("#po_number").val(number);
        $("#supplier").val(supplier);
        $("#warehouse").val(warehouse);
        $("#remarks").val(remarks);
        
        $.ajax({
            url: '/iwms/api/purchase-orders/'+ po_id + '/products',
            type: 'GET',
            contentType: "application/json; charset=utf-8",
            success: function(data){
                for (i=0; i < data.items.length;  ++i){
                    var row = table_po_line.row.add([
                    data.items[i].id,
                    data.items[i].number,
                    data.items[i].name,
                    data.items[i].uom,
                    data.items[i].qty,
                    data.items[i].received_qty,
                    data.items[i].remaining_qty
                    ]);
                    table_po_line.row(row).column(0).nodes().to$().addClass('myHiddenColumn');
                    if (data.items[i].remaining_qty == 0){
                        table_po_line.row(row).nodes().to$().addClass('list-group-item-success');
                    }else if(data.items[i].qty == data.items[i].remaining_qty){
                        table_po_line.row(row).nodes().to$().addClass('list-group-item-danger');
                    }else{
                        table_po_line.row(row).nodes().to$().addClass('list-group-item-warning');
                    }
                    table_po_line.row(row).draw();
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