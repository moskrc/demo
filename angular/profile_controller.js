'use strict';

angular.module('main').controller('ProfileController', ['$scope', '$timeout', 'CurrentGameService', 'CurrentUserService', '$filter', '$rootScope', 'toaster', function ($scope, $timeout, CurrentGameService, CurrentUserService, $filter, $rootScope, toaster) {

}]).controller('ProfileChangePasswordController', ['$scope', '$http', '$timeout', 'CurrentGameService', 'CurrentUserService', '$filter', '$rootScope', 'toaster', function ($scope, $http, $timeout, CurrentGameService, CurrentUserService, $filter, $rootScope, toaster) {

    $scope.alerts = [];
    $scope.user = null;

    CurrentUserService.get(function (data) {
        $scope.user = data;
    });

    $scope.submit = function (user) {
        $http.post('/api/change_password/',
            {
                'username': user.username,
                'password': user.current_password,
                'new_password': user.new_password
            },
            {
                headers: {'Content-Type': 'application/json'}
            }
        ).success(function (data, status, headers, config) {
                toaster.pop('success', 'Success');

                if ($rootScope.app_version > 1.7) {
                    engine.call('xSetPassword', user.new_password);
                }

                $scope.user.current_password = null;
                $scope.user.new_password = null;
                $scope.user.confirm_password = null;
                $scope.ChangePasswordForm.$setPristine();
            }).error(function (data, status, headers, config) {
                if (data.non_field_errors) {
                    toaster.pop('error', data.non_field_errors[0]);
                } else {
                    toaster.pop('error', 'Error');
                }
            });

    };


}]).controller('UploadController', ['$scope', '$timeout', 'CurrentGameService', 'CurrentUserService', 'CurrentUserPerGameService', '$filter', '$rootScope', 'toaster', '$log', function ($scope, $timeout, CurrentGameService, CurrentUserService, CurrentUserPerGameService, $filter, $rootScope, toaster, $log) {
    var log = $log.getInstance('profile_controller');

    $scope.alerts = [];
    $scope.user = null;
    $scope.oldUser = null;

    CurrentUserService.get(function (data) {
            CurrentUserPerGameService.get(function(data_settings) {
            $scope.user = data;
            $scope.oldUser = angular.copy($scope.user);
            $scope.settings = data_settings;
        });


    });

    $scope.submit = function (user) {
        console.log($scope.user)

        if ($rootScope.app_version > 1.7) {
            if (user.username != $scope.oldUser.username) {
                engine.call('xSetUserName', user.username)
            }
        }

        $scope.user = angular.copy(user);
        $scope.oldUser = angular.copy(user);

        var changed_user = angular.copy(user);

        console.log(changed_user.avatar)
        if (changed_user.avatar) {
            changed_user.avatar = changed_user.avatar.id
        }
        console.log('ssx')
        console.log(changed_user.avatar)
        console.log(changed_user)
        console.log('ssx')

        changed_user.$save(function (successResult) {
            toaster.pop('success', "Success");
        }, function (errorResult) {
            toaster.pop('error', errorResult.statusText);
        });

    };
}]);