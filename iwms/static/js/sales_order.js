$(document).ready(function(){
    var table_sr = $('#tbl_client_modal').DataTable({
        "pageLength": 8
    });

    var table_product_line = $('#tbl_product_modal').DataTable({
        "order": [[2,'asc']]
    });

    $("#tbl_client_modal").on('click','tr',function(){
        $(this).addClass('selected').siblings().removeClass('selected');    
     });

    $('#btn_select_client').click(function(){
        var client = $("#tbl_client_modal tr.selected td:nth-child(3)").html();
        var term = $("#tbl_client_modal tr.selected td:nth-child(4)").html();
        var ship_via = $("#tbl_client_modal tr.selected td:nth-child(5)").html();
        $("#client_name").val(client);
        $("#term").val(term);
        $("#ship_via").val(ship_via);
    });

    $("#btn_add_product").click(function(){
        var csrf_token = "{{ csrf_token() }}";
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrf_token);
                }
            }
        });
        $("tr").each(function() {
            var check = $(this).find("input.chkbox").is(':checked');
            if(check){
                var item_no = $(this).find("td").eq(2).html();
                var item_name = $(this).find("td").eq(3).html();
                var item_description = $(this).find("td").eq(4).html();
                var item_id = $(this).find("td").eq(0).html();
                var item_available_qty = $(this).find("td").eq(6).html();
                var item_expiry_date = $(this).find("td").eq(5).html();
                var item_price = $(this).find("td").eq(7).html();
                var item_uom = `<select name="uom_${item_id}" style='width':100%;'>`;
                    $.ajax({
                        url: "/iwms/_get_uom_line",
                        type: 'POST',
                        async: false,
                        dataType: 'json',
                        data: JSON.stringify({'stock_item_id':0}),
                        contentType: "application/json; charset=utf-8",
                        success: function(data){
                            for (i=0; i < data.uom_lines.length; ++i){
                                item_uom += `<option value='${data.uom_lines[i].id}'>${data.uom_lines[i].code}</option>`;
                            }
                        }
                    });
                var _trim_item_available_qty = $.trim(item_available_qty);
                $('#tbl_so_line tr:last').after(
                    `<tr>
                        <td style="display:none;"><input name="products[]" type="hidden" value="${item_id}"></td>
                        <td style="display:none;">${item_description}</td>
                        <td style="display:none;">${item_expiry_date}</td>
                        <td><input class="chkbox" type="checkbox"></td>
                        <td class='text-center'>${item_no}</td>
                        <td class='text-center'>${item_name}</td>
                        <td class='text-center'>${item_uom}</td>
                        <td class='text-center'><input class="input_qty" max="${_trim_item_available_qty}" name="qty_${item_id}" type="number" style="width:100px" value="0"></td>
                        <td class='text-center'>${item_available_qty}</td>
                        <td class='text-center'><input class="input_price" name="price_${item_id}" type="number" value="${item_price}" style="width:100px"></td>
                        <td class='text-center'><input class="input_subtotal" name="subtotal_${item_id}" type="number" value="0.00" style="width:100px" readonly></td>
                    </tr>
                    `
                    );
                table_product_line.row($(this)).remove().draw();
            }
        });
    });

    $("#btn_delete_line").click(function(){
        $("#tbl_so_line tr").each(function() {
            var check = $(this).find("input.chkbox").is(':checked');
            if (check){
                var row = table_product_line.row.add([
                    $(this).find("input").eq(0).val(),
                    "<input class='chkbox' type='checkbox'>",
                    $(this).find("td").eq(4).html(),
                    $(this).find("td").eq(5).html(),
                    $(this).find("td").eq(1).html(),
                    $(this).find("td").eq(2).html(),
                    $(this).find("td").eq(8).html(),
                    $(this).find("input").eq(3).val(),
                ]);
                table_product_line.row(row).column(0).nodes().to$().addClass('myHiddenColumn');
                table_product_line.row(row).column(7).nodes().to$().addClass('myHiddenColumn');
                table_product_line.row(row).draw();
                $(this).remove();
            }
        });
    });
    $('#tbl_so_line').on('change', 'input', function(){
        var row = $(this).closest("tr");
        var price = row.find('.input_price').val();
        var qty = row.find('.input_qty').val();
        var amount = parseFloat(qty) * parseFloat(price); 
        row.find('.input_subtotal').val(amount.toFixed(2));
        var total = 0;
        $("#tbl_so_line tr").each(function() {
            if ($(this).find("input").eq(0).val()){
                var subtotal = $(this).find("input").eq(4).val();
                total += parseFloat(subtotal);
                $("#p_total").html(`<strong>TOTAL: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</strong>${total}`);
            }
        });
    });

    var _total = 0
    
    $("#tbl_so_line tr").each(function() {
        var row = $(this).closest("tr");
        var price = row.find('.input_price').val();
        var qty = row.find('.input_qty').val();
        var amount = parseFloat(qty) * parseFloat(price); 
        row.find('.input_subtotal').val(amount.toFixed(2));
        var _total = 0;
        $("#tbl_so_line tr").each(function() {
            if ($(this).find("input").eq(0).val()){
                var subtotal = $(this).find("input").eq(4).val();
                _total += parseFloat(subtotal);
                $("#p_total").html(`<strong>TOTAL: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</strong>${_total}`);
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