console.log("Hi");

var app = angular.module('filtersearchApp', []);
console.log("H2");
// Change Angular special bracets because they collide with Jinja :-) - Anja 4.4.2017
// It is also possible to use the following expression and do not change angualr delimiters:
// {{ '{{myname}}' }}
app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{ang');
  $interpolateProvider.endSymbol('ang}');
}]);
app.controller('MainCtrl', ['$scope', function ($scope) {
  $scope.itemlist = null;
  $scope.init = function(value) {
    if (!value)
      return;
    $scope.itemlist = value;
    $scope.fmin =10;
    $scope.fmax = 100;
    $scope.illen = value.length;

   for (var i =0; i <value.length;i++)
      console.log(value[i]);
  }
}]);
