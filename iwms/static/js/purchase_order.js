$(document).ready(function(){

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    var table_product = $('#tbl_product_modal').DataTable({
    });
    var pe_supplier_id = $("#supplier_id").val();
    var pe_po_number = $("#po_generated_number").contents().filter(function(){ 
        return this.nodeType == 3; 
      })[0].nodeValue.trim();


    $('#tbl_line_items').on('change', 'input', function(){
        var row = $(this).closest("tr");
        var cost = row.find('.input_cost').val();
        var qty = row.find('.input_qty').val();
        var amount = parseFloat(qty) * parseFloat(cost); 
        row.find('.amount').val(amount.toFixed(2));
    });
    

    $.ajax({
        url: "/iwms/api/get-supplier-products?sup_id=" + pe_supplier_id + "&po_number=" + pe_po_number,
        type: "GET",
        contentType: "application/json; charset=utf-8",
        success: function(data) {
            for(i=0;i < data.items.length; ++i){
                var row = table_product.row.add([
                data.items[i].id,
                data.items[i].default_cost,
                "<input class='chkbox' type='checkbox'>",
                data.items[i].number,
                data.items[i].name,
                data.items[i].description,
                data.items[i].barcode
                ]);
                table_product.row(row).column(0).nodes().to$().addClass('myHiddenColumn');
                table_product.row(row).column(1).nodes().to$().addClass('myHiddenColumn');
                table_product.row(row).draw();
            }
        }
    });


    $("#supplier_id").change(function(){
        var supplier_id = $(this).val();
     
        $.ajax({
            url: "/iwms/api/get-supplier-products?sup_id=" + supplier_id,
            type: "GET",
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                table_product.clear().draw();
                $("#tbl_line_items tr").each(function() {
                    if ($(this).find("input").eq(0).val()){
                        $(this).remove();
                    }
                });

                for(i=0;i < data.items.length; ++i){
                    var row = table_product.row.add([
                    data.items[i].id,
                    data.items[i].default_cost,
                    "<input class='chkbox' type='checkbox'>",
                    data.items[i].number,
                    data.items[i].name,
                    data.items[i].description,
                    data.items[i].barcode
                    ]);
                    table_product.row(row).column(0).nodes().to$().addClass('myHiddenColumn');
                    table_product.row(row).column(1).nodes().to$().addClass('myHiddenColumn');
                    table_product.row(row).draw();
                }
            }
        });
    });

    
    $("#btn_add_product").click(function(){
        $("tr").each(function() {
            var check = $(this).find("input.chkbox").is(':checked');

            if(check){
                var item_no = $(this).find("td").eq(3).html();
                var item_name = $(this).find("td").eq(4).html();
                var item_description = $(this).find("td").eq(5).html();
                var item_id = $(this).find("td").eq(0).html();
                var item_barcode = $(this).find("td").eq(6).html();
                var item_default_cost = $(this).find("td").eq(1).html();
                var item_uom = `<select name="uom_${item_id}" style='width':100%;'>`;
            
                $.ajax({
                    url: "/iwms/api/get-product-uom-line?stock_item_id=" + item_id,
                    type: 'GET',
                    async: false,
                    contentType: "application/json; charset=utf-8",
                    success: function(data){
                        for (i=0; i < data.uom_lines.length; ++i){
                            if (data.uom_lines[i].default == 'true'){
                                item_uom += `<option value='${data.uom_lines[i].id}' selected>${data.uom_lines[i].code}</option>`;
                            }else{
                                item_uom += `<option value='${data.uom_lines[i].id}'>${data.uom_lines[i].code}</option>`;
                            }
                        }
                    }
                });

                $('#tbl_line_items tr:last').after(
                    `<tr>
                        <td style="display:none;"><input name="products[]" type="hidden" value="${item_id}"></td>
                        <td style="display:none;">${item_description}</td>
                        <td style="display:none;">${item_barcode}</td>
                        <td><input class="chkbox" type="checkbox"></td>
                        <td class='text-center'>${item_no}</td>
                        <td class='text-center'>${item_name}</td>
                        <td class='text-center'>
                            ${item_uom}
                            </select>
                        </td>
                        <td class='text-center'><input class="input_qty" name="qty_${item_id}" type="number" style="width:100px" value="0"></td>
                        <td class='text-center'><input class="input_cost" name="cost_${item_id}" type="number" value="${item_default_cost}" style="width:100px" readonly></td>
                        <td class='text-center'><input class="amount" name="amount_${item_id}" type="number" value="0.00" style="width:100px" readonly></td>
                    </tr>
                    `
                    );
                table_product.row($(this)).remove().draw();
            }
        });
    });
    

    $("#btn_delete_line").click(function(){
        $("#tbl_line_items tr").each(function() {
            var check = $(this).find("input.chkbox").is(':checked');
            if (check){
                var row = table_product.row.add([
                    $(this).find("input").eq(0).val(),
                    $(this).find("input").eq(3).val(),
                    "<input class='chkbox' type='checkbox'>",
                    $(this).find("td").eq(4).html(),
                    $(this).find("td").eq(5).html(),
                    $(this).find("td").eq(1).html(),
                    $(this).find("td").eq(2).html()
                ]);
                table_product.row(row).column(0).nodes().to$().addClass('myHiddenColumn');
                table_product.row(row).column(1).nodes().to$().addClass('myHiddenColumn');
                table_product.row(row).draw();
                $(this).remove();
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