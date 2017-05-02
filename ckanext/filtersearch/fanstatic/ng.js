//console.log("Hi");

var app = angular.module('filtersearchApp', []);
//console.log("H2");
// Change Angular special bracets because they collide with Jinja :-) - Anja 4.4.2017
// It is also possible to use the following expression and do not change angular delimiters:
// {{ '{{myname}}' }}
app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{ang');
  $interpolateProvider.endSymbol('ang}');
}]);
app.controller('MainCtrl', ['$scope', function ($scope) {
  $scope.facetMinLimit = 10;
  $scope.facetMaxLimit = 100;


  $scope.itemlist = "";

  $scope.init = function(value) {

    if (!value)
      return;

  //console.log(value);

  $scope.itemlist = value;
  $scope.fmin =10;
  $scope.fmax = 100;
  $scope.illen = value.length;
  $scope.limit =10;



  }
}]);
