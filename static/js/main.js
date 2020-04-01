var shoppingCart = (function() {
  cart = [];

  // Constructor
  function Item(name, price, count) {
    this.name = name;
    this.price = price;
    this.count = count;
  }

  // Save cart
  function cartSave() {
    sessionStorage.setItem('shoppingCart', JSON.stringify(cart));
  }

    // Load cart
  function cartLoad() {
    cart = JSON.parse(sessionStorage.getItem('shoppingCart'));
  }
  if (sessionStorage.getItem("shoppingCart") != null) {
    cartLoad();
  }

  var obj = {};

  // Add to cart
  obj.addToCart = function(name, price, count) {
    for(var item in cart) {
      if(cart[item].name === name) {
        cart[item].count ++;
        cartSave();
        return;
      }
    }
    var item = new Item(name, price, count);
    cart.push(item);
    cartSave();
  }
  // Set count from item
  obj.setCountItem = function(name, count) {
    for(var i in cart) {
      if (cart[i].name === name) {
        cart[i].count = count;
        break;
      }
    }
  };
  // Remove item from cart
  obj.removeItemCart = function(name) {
    for(var item in cart) {
      if(cart[item].name === name) {
        cart[item].count --;
        if(cart[item].count === 0) {
          cart.splice(item, 1);
        }
        break;
      }
    }
    cartSave();
  }

  // Remove all items from cart
  obj.removeItemAll = function(name) {
    for(var item in cart) {
      if(cart[item].name === name) {
        cart.splice(item, 1);
        break;
      }
    }
    cartSave();
  }

  // Clear cart
  obj.cartClear = function() {
    cart = [];
    cartSave();
  }

  // Count cart
  obj.countTotal = function() {
    var countTotal = 0;
    for(var item in cart) {
      countTotal += cart[item].count;
    }
    return countTotal;
  }

  // Total cart
  obj.cartTotal = function() {
    var cartTotal = 0;
    for(var item in cart) {
      cartTotal += cart[item].price * cart[item].count;
    }
    return Number(cartTotal.toFixed(2));
  }

  // List cart
  obj.cartList = function() {
    var cartCopy = [];
    for(i in cart) {
      item = cart[i];
      itemCopy = {};
      for(p in item) {
        itemCopy[p] = item[p];
      }
      itemCopy.total = Number(item.price * item.count).toFixed(2);
      cartCopy.push(itemCopy)
    }
    return cartCopy;
  }
  return obj;
})();

$('.add-to-cart').click(function(event) {
  event.preventDefault();
  var name = $(this).data('name');
  var price = Number($(this).data('price'));
  shoppingCart.addToCart(name, price, 1);
  cartDisplay();
});

// Clear items
$('.clear-cart').click(function() {
  shoppingCart.cartClear();
  cartDisplay();
});

function cartDisplay() {
  var arrayCart = shoppingCart.cartList();
  var output = "";
  var dataCart = [];
  var countCart = [];
  for(var i in arrayCart) {
    output += "<tr>"
      + "<td>" + arrayCart[i].name + "</td>"
      + "<td>(" + arrayCart[i].price + ")</td>"
      + "<td><div class='input-group'><input type='number' class='item-count form-control' data-name='" + arrayCart[i].name + "' value='" + arrayCart[i].count + "'>" + "</div></td>"
      + "<td><button class='delete-item btn btn-danger' data-name=" + arrayCart[i].name + ">X</button></td>"
      + " = "
      + "<td width='100'>" + arrayCart[i].total + "</td>"
      +  "</tr>";
    dataCart.push(arrayCart[i].name);
    countCart.push(arrayCart[i].count);
  }
  var formData = "<input hidden name='item' type='text' value="+dataCart+" /> <input hidden name='count' type='text' value="+countCart+" />"

  $('.show-cart tbody').html(output);
  $('.payment-input').html(formData)
  $('.total-cart').html(shoppingCart.cartTotal());
  $('.total-count').html(shoppingCart.countTotal());
}

// Delete item button
$('.show-cart').on("click", ".delete-item", function(event) {
  var name = $(this).data('name')
  shoppingCart.removeItemAll(name);
  cartDisplay();
})


// Item count input
$('.show-cart').on("change", ".item-count", function(event) {
   var name = $(this).data('name');
   var count = Number($(this).val());
  shoppingCart.setCountItem(name, count);
  cartDisplay();
});

cartDisplay();

// Datatable https://datatables.net/examples/styling/bootstrap4.html for pagination
$(document).ready(function() {
    if(window.location.pathname == '/payment') {
       shoppingCart.cartClear();
       cartDisplay();
    }
    $('#pagination').DataTable();
});

function hideLoader() {
    $('#loading').hide();
}
$(window).ready(hideLoader);

setTimeout(hideLoader, 20 * 1000);
