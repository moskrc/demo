'use strict';


var app = angular.module('main');


// index
app.controller('MultiPlayerTournamentController', ['$scope', '$rootScope', '$log', 'TournamentService', 'toaster', function ($scope, $rootScope, $log, TournamentService, toaster) {
    var log = $log.getInstance('tournament_controller');
    $scope.loaded = false;

    $scope.init = function () {

        // called from challenge directive, initialize the controller
        log.debug('init');

        TournamentService.get({'game_id': $rootScope.my_info.game_id}, function (data) {
            $scope.tournaments = data.results;
            $scope.loaded = true;

        }, function (data) {
            toaster.pop('error', data.statusText);
        })

    }

    $scope.init();

}])

// new
app.controller('MultiPlayerTournamentControllerNew', ['$scope', '$state', '$interval', '$timeout', 'CurrentGameService', '$filter', '$rootScope', '$log', 'MatchService', 'TournamentService', 'toaster', function ($scope, $state, $interval, $timeout, CurrentGameService, $filter, $rootScope, $log, MatchService, TournamentService, toaster) {
    var log = $log.getInstance('tournament_controller_new');
    var new_tournament_id = null;

    $scope.init = function () {

        log.debug('init');

        $scope.formData = {'capacity': 4}

        $('#new_dlg').modal('toggle').on('hidden.bs.modal', function () {
            if (new_tournament_id) {
                $state.transitionTo('multi_player_tournament_view', {'tournamentId': new_tournament_id})
            } else {
                $state.transitionTo('multi_player_tournament')
            }
        });
    }

    $scope.init()

    $scope.processForm = function () {
        console.log('process')
        TournamentService.save({'game_id': $rootScope.my_info.game_id}, {
            'title': $scope.formData.title,
            'capacity': $scope.formData.capacity,
            'players': []
        }, function (data) {
            // success
            $scope.errorTitle = $scope.errorCapacity = false;
            toaster.pop('success', "Success");
            $('#new_dlg').modal('toggle');
            new_tournament_id = data.id;
        }, function (data) {
            // error
            $scope.errorTitle = data.data.title;
            $scope.errorCapacity = data.data.capacity;
        });

    };
}])


// view
app.controller('MultiPlayerTournamentControllerView', ['$scope', '$interval', '$timeout', 'Socket', 'CurrentGameService', '$filter', '$rootScope', '$log', 'MatchService', 'TournamentService', '$stateParams', 'toaster', '$http', function ($scope, $interval, $timeout, socket, CurrentGameService, $filter, $rootScope, $log, MatchService, TournamentService, $stateParams, toaster, $http) {
    var log = $log.getInstance('tournament_controller_view');
    $scope.joined = false;

    $rootScope.my_info['mode'] = 'tournament_' + $stateParams.tournamentId;
    socket.emit('join', $rootScope.my_info);

    socket.socket.removeListener('msg_to_room');

    socket.on('msg_to_room', function (data, message) {
        console.log(data, message)
        if (data.action == 'tournament_slots_update' && data.data.from.id != $rootScope.my_info.id) {
            update_slots()
        }
    });


    var update_slots = function () {

        TournamentService.get({'game_id': $rootScope.my_info.game_id, 'id': $stateParams.tournamentId}, function (data) {
            $scope.tournament = data;
            $scope.slots = new Array();

            $scope.joined = false;

            for (var i = 0; i < data.capacity; i++) {
                $scope.slots[i] = data.players_info[i] || null;

                if ($scope.slots[i]) {
                    if ($scope.slots[i].id == $rootScope.my_info.id) {
                        $scope.joined = true
                    }
                }
            }

            console.log($scope.slots)

            angular.forEach($scope.slots, function (value, i) {
                console.log(value, i)
            })

        }, function (data) {
            toaster.pop('error', data.statusText);
        })

    }

    $scope.init = function () {

        log.debug('init');
        update_slots()
    }

    $scope.init();


    var check_for_full = function () {
//        if ($scope.tournament.capacity > 0 && $scope.tournament.empty == 0) {
//
//        }
        // sside
    }


    $scope.join_unjoin = function (suffix) {
        $http({
            url: '/api/games/' + $rootScope.my_info.game_id + '/tournaments/' + $stateParams.tournamentId + '/' + suffix,
            method: "POST",
            data: {'user_id': $rootScope.my_info.id},
            headers: {'Content-Type': 'application/json'}
        }).success(function (data, status, headers, config) {
            socket.emit('user_message', {'action': 'tournament_slots_update', 'data': {'from': $rootScope.my_info, 'event': data.status}});
            toaster.pop('success', 'Successfully');
            update_slots()
            check_for_full()
        }).error(function (data, status, headers, config) {
            toaster.pop('error', data.statusText);
        });
    }


}]);


app.controller('MultiPlayerTournamentControllerChallenge', ['$scope', '$interval', '$timeout', 'Socket', 'CurrentGameService', '$filter', '$rootScope', '$log', 'MatchService', 'TournamentService', '$stateParams', 'toaster', '$http', function ($scope, $interval, $timeout, socket, CurrentGameService, $filter, $rootScope, $log, MatchService, TournamentService, $stateParams, toaster, $http) {
    var log = $log.getInstance('tournament_controller_challenge');

    TournamentService.get({'game_id': $rootScope.my_info.game_id, 'id': $stateParams.tournamentId}, function (data) {
        $scope.tournament = data;

        MatchService.get({'game_id': $rootScope.my_info.game_id, 'tournament_id': $stateParams.tournamentId, 'id': $stateParams.matchId}, function (data) {
            $scope.match = data;


            if ($scope.match.player2.id == $rootScope.my_info.id) {
                var opponent_id = $scope.match.player1.id;
            } else {
                var opponent_id = $scope.match.player2.id;
            }

            socket.emit('background_message', {'action': 'invite', 'message': {'to': opponent_id, 'from': $rootScope.my_info, 'tournament': $scope.tournament, 'match': $scope.match }, 'room': 'game_' + $rootScope.current_game.id});


        });


    }, function (data) {
        toaster.pop('error', data.statusText);
    });


}]);