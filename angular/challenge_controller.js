'use strict';

function sortByKey(array, key) {
    return array.sort(function(a, b) {
        var x = a[key]; var y = b[key];
        return ((x < y) ? -1 : ((x > y) ? 1 : 0));
    });
}

angular.module('main').controller('MultiPlayerChallengeController', ['$scope', '$interval', '$timeout', 'Socket', 'CurrentGameService', 'CurrentUserService', 'CurrentUserPerGameService', '$filter', '$rootScope', '$log', 'MatchServiceMP', 'toaster', function ($scope, $interval, $timeout, socket, CurrentGameService, CurrentUserService, CurrentUserPerGameService, $filter, $rootScope, $log, MatchServiceMP, toaster) {

    var log = $log.getInstance('challenge_controller');
    var timer = null;
    var timer_unity = null;
    var selected_mode = null;
    var room = null;

//    // don't remove this yet
//    $scope.test_gumballs = function(){
//        $rootScope.my_info.full_info.settings.data.gumballs=22;
//        CurrentUserPerGameService.save({'game_id': $rootScope.my_info.game_id, 'user_id': $rootScope.my_info.id}, $rootScope.my_info.full_info.settings);
//        socket.emit('update_my_info', $rootScope.my_info);
//    }

    if ($rootScope.app_version!= '1.0' &&  $rootScope.app_version < 1.7) {
        //toaster.pop('success', "Please update your app to version 1.8 to play multiplayer games with everyone!");
        $('#upgrade_dlg').modal('toggle');
    }

    var getCompetitor = function () {
        if ($scope.challenge.user1.id == $rootScope.my_info.id) {
            var competitor = $scope.challenge.user2;
        } else {
            var competitor = $scope.challenge.user1;
        }

        return competitor
    }

    var guid = function () {
        function s4() {
            return Math.floor((1 + Math.random()) * 0x10000)
                .toString(16)
                .substring(1);
        }

        return function () {
            return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
                s4() + '-' + s4() + s4() + s4();
        };
    };


    var findTheBestServer = function(game) {
        log.info('--- finding a nearest server')
        var best_server = null;

        var servers = [];

        for (var x = 0; x < game.servers.length; x++) {
            var server = game.servers[x];
            if (server.type == 1) { // client server
                console.log(server)
                log.info('Ping ' + server.ip + '...')

                var startTime, endTime, totalTime = null;

                $.ajax({
                    url: 'http://' + server.ip,
                    async: false,

                    beforeSend: function () {
                        startTime = new Date();
                    },
                    success: function () {
                        endTime = new Date();
                        totalTime = endTime - startTime;
                        servers.push({'ping': totalTime, 'server': server})
                        log.info('Total Time ' + totalTime)
                    }
                })
            }
        }

        log.info('Tested servers')
        log.info(servers);

        sortByKey(servers, 'ping')

        if (servers.length > 0) {
            best_server = servers[0]
        } else {
            best_server = null
        }

        log.info('--- the best server is ' + best_server.server.ip + '(' + best_server.ping + ')')

        log.info('--- finding a nearest server end')

        if (best_server) {
            return best_server.server
        } else {
            return null
        }
    }


    $scope.onlineUsers = []
    $scope.challenge = {
        'user1': null,
        'user2': null,
        'mode': 'unknown',
        'client': null,
        'server': null,
        'gumballs':0
    }


    $scope.init = function (mode, match_id) {

        // called from challenge directive, initialize the controller
        log.debug('init');
        log.debug(match_id)
        selected_mode = mode;

        $scope.title = selected_mode;
        $scope.match_id = match_id;

        log.debug('Call to UNITY, request for local ip...');
        engine.call('xGetMyLocalIP');

        if (mode == 'server') {
            log.debug('Server Mode')
        } else if (mode == 'lan') {
            log.debug('LAN Mode')
        } else if (mode == 'bluetooth') {
            log.debug('Bluetooth Mode')
            log.debug('Call to UNITY, request for my bluetooth name and a list of nearby devices that my device found via bluetooth...');
            engine.call('xGetMyBluetoothInfo');
        } else {
            log.debug('Unknown mode')
            $scope.title = 'unknown'
        }

        $rootScope.my_info['mode'] = selected_mode;
        $rootScope.my_info['is_online'] = true;

        CurrentGameService.get(function(data) {
            $rootScope.current_game = data;

            if (match_id) {
                room = 'game_' + $rootScope.current_game.id + '_' + mode + '_match_id_' + match_id;
            } else {
                room = 'game_' + $rootScope.current_game.id + '_' + mode;
            }

            CurrentUserService.get(function (data) {

                $rootScope.my_info.full_info = data;

                CurrentUserPerGameService.get(function (data) {

                    $rootScope.my_info.full_info.settings = data;

                    log.debug('Try to join')
                    socket.emit('subscribe', {'user': $rootScope.my_info, 'room': room, 'user_id': $rootScope.my_info.id});

                });
            });
        });




        var filter_users = function (data) {
            var res = [];
            log.debug('update users list')

            for (var u in data) {
                if (data[u].id != $rootScope.my_info.id) {
                    // It's not me
                    console.log(data[u])
                    if (data[u].is_online) {
                        if ($rootScope.my_info['mode'] == 'server') {
                            res.push(data[u])
                        } else if ($rootScope.my_info['mode'] == 'lan') {
                            if (data[u].public_ip && data[u].public_ip == $rootScope.my_info.public_ip) {
                                res.push(data[u])
                            }
                        } else if ($rootScope.my_info['mode'] == 'bluetooth') {
                            if (data[u].bluetooth_name && (($.inArray(data[u].bluetooth_name, $rootScope.my_info.bluetooth_nearby_devices) > -1) && ($.inArray($rootScope.my_info.bluetooth_name, data[u].bluetooth_nearby_devices) > -1))) {
                                res.push(data[u])
                            }
                        } else {
                            alert('Unknown mode');
                        }
                    }
                }
            }

            return res;
        }

        socket.socket.removeListener('msg_to_room');
        socket.socket.removeListener('update_users');

        socket.on('update_users', function (data, in_room) {

            console.log(data, in_room, room)
            if (room == in_room) {
                log.debug('on update users, data ' + angular.toJson(data));
                $scope.onlineUsers = filter_users(data);
            }
        });


        $scope.fsm = StateMachine.create({
            initial: 'ready',
            events: [
                // invite an user and go to requesting state
                { name: 'bet', from: 'ready', to: 'betting' },
                { name: 'invite', from: 'betting', to: 'requesting' },
                // response on invite and go to answering state
                { name: 'answer', from: 'ready', to: 'answering' },
                // accept challenge and go to connecting state
                { name: 'accept', from: ['requesting', 'answering'], to: 'connecting_to_unity'},
                // reject challenge and go to rejected state
                { name: 'reject', from: ['requesting', 'answering'], to: 'rejected'},

                { name: 'connected_to_unity', from: 'connecting_to_unity', to: 'connecting'},

                { name: 'try_p2p', from: 'connecting', to: 'connecting_p2p'},
                { name: 'try_server', from: ['connecting', 'try_p2p'], to: 'connecting_server'},

                { name: 'cant_play', from: ['connecting_p2p', 'connecting_server', 'connecting_to_unity', 'connecting'], to: 'failed'},
                //{ name: 'startgame', from: ['connecting_p2p', 'connecting_server', 'connecting'], to: 'starting'},
                { name: 'startgame', from: '*', to: 'starting'}, //testing


                // play, pause, quit
                { name: 'play', from: ['starting', 'pausing', 'ready_pause'], to: 'playing'},
                { name: 'pause', from: 'playing', to: 'pausing'},
                { name: 'wait_pause', from: 'playing', to: 'ready_pause'},
                { name: 'quit', from: ['pausing', 'ready_pause' ], to: 'quitting'},


                { name: 'reset', from: ['*'], to: 'ready' }
            ],
            callbacks: {
                // ===========================================================
                onready: function () {
                    log.info('onready');
                    $scope.count_down_timer = 15; // 15 sec

                    $rootScope.my_info['is_online'] = true;
                    socket.emit('update_my_info', $rootScope.my_info);

                    $scope.challenge = {
                        'user1': null,
                        'user2': null,
                        'mode': 'unknown',
                        'client': null,
                        'server': null,
                        'match_id': $scope.match_id
                    }

                    $scope.selected_user = null;

                    $scope.isSelected = function (user) {
                        return $scope.selected_user === user;
                    }

                    $scope.getSelectedUser = function () {
                        return $scope.onlineUsers[$scope.selected_user] || null
                    }

                    $scope.selectUser = function (selected_user) {
                        log.info('selectUser: ' + selected_user);
                        $scope.selected_user = selected_user;

                        $scope.challenge.user1 = $rootScope.my_info
                        $scope.challenge.user2 = $scope.getSelectedUser()
                        $scope.challenge.guid = guid()();

                        $scope.fsm.bet();
                    }

                    socket.socket.removeListener('msg_to_room');


                    socket.on('msg_to_room', function (msg) {
                        log.debug('1 on msg_to_room: ' + angular.toJson(msg))

                        // answer to request
                        if (msg.action == 'challenge_request') {
                            if (msg.data.user2.id == $rootScope.my_info.id) {
                                $scope.challenge = msg.data;
                                $scope.fsm.answer();
                            }
                        }
                    });
                },
                // ===
                onbetting: function() {

                    if (mode == 'server') {
                        if (!$rootScope.my_info.nearest_server) {
                            $rootScope.my_info.nearest_server = findTheBestServer($rootScope.current_game)
                            $scope.challenge.nearest_server = $rootScope.my_info.nearest_server;
                        }
                        log.info('Nearest server is '+$rootScope.my_info.nearest_server.ip);
                    }

                    $scope.mybets = 10;

                    $scope.changeBet = function(val) {

                        $scope.mybets+=val;

                        if ($scope.mybets > $rootScope.my_info.full_info.settings.data.gumballs){
                            $scope.mybets = $rootScope.my_info.full_info.settings.data.gumballs;
                        }

                        if ($scope.mybets > $scope.challenge.user2.full_info.settings.data.gumballs){
                            $scope.mybets = $scope.challenge.user2.full_info.settings.data.gumballs;
                        }

                        if ($scope.mybets < 0) {
                            $scope.mybets = 0;
                        }
                    }

                    $rootScope.my_info['is_online'] = false;
                    log.error('OFFLINE: ' + angular.toJson($rootScope.my_info));
                    socket.emit('update_my_info', $rootScope.my_info);

                    $scope.invite = function() {
                        $scope.challenge.gumballs = $scope.mybets;
                        socket.emit('user_message', {'action': 'challenge_request', 'data': $scope.challenge, 'room': room });
                        log.error('invite user, data: ' + angular.toJson($scope.challenge))
                        $scope.fsm.invite(); // onrequesting
                    }

                    $scope.cancelChallenge = function () {
                        log.debug('cancelChallenge');
                        $scope.selected_user = null;
                        $scope.fsm.reset();
                        return true;
                    }

                    if ($rootScope.current_game.is_live) {
                        $scope.invite();
                    }


                },
                // ===========================================================
                onrequesting: function () {
                    log.info('onrequesting');

                    $scope.cancelChallenge = function () {
                        log.debug('cancelChallenge');
                        $scope.selected_user = null;
                        socket.emit('user_message', {'action': 'challenge_cancel', 'data': $scope.challenge, 'room': room});
                        $scope.fsm.reset();
                        return true;
                    }

                    socket.socket.removeListener('msg_to_room');
                    socket.on('msg_to_room', function (msg) {
                        log.debug('2 on msg_to_room: ' + angular.toJson(msg))

                        if (msg.action == 'challenge_accepted') {
                            if (msg.data.user1.id == $rootScope.my_info.id) {
                                $scope.challenge = msg.data;
                                $scope.fsm.accept();

                            }
                        }

                        if (msg.action == 'challenge_rejected') {
                            if (msg.data.user1.id == $rootScope.my_info.id) {
                                $scope.challenge = msg.data;
                                $scope.fsm.reject();

                            }
                        }

                    });

                },
                // ===========================================================
                onanswering: function () {
                    log.info('onanswering');

                    $rootScope.my_info['is_online'] = false;
                    socket.emit('update_my_info', $rootScope.my_info);

                    $scope.acceptChallenge = function () {
                        log.debug('acceptChallenge');
                        socket.emit('user_message', {'action': 'challenge_accepted', 'data': $scope.challenge, 'room': room});
                        $scope.fsm.accept();
                        //startGame('xEstablishMPGameReceive');
                        return true;
                    }

                    $scope.rejectChallenge = function () {
                        log.debug('rejectChallenge');
                        socket.emit('user_message', {'action': 'challenge_rejected', 'data': $scope.challenge, 'room': room});
                        $scope.fsm.reset();
                        return true;
                    }

                    socket.socket.removeListener('msg_to_room');

                    socket.on('msg_to_room', function (msg) {
                        log.debug('3 on msg_to_room: ' + angular.toJson(msg))

                        if (msg.action == 'challenge_cancel') {
                            if (msg.data.user2.id == $rootScope.my_info.id) {
                                $scope.fsm.reset();
                            }
                        }

                    });

                },
                // ===========================================================
                onrejected: function () {
                    log.info('onrejected');
                },
                // ===========================================================
                onconnecting_to_unity: function () {
                    log.info('onconnecting');

                    var response_received = false;

                    if ($scope.challenge.user1.id == $rootScope.my_info.id) {
                        var competitor = $scope.challenge.user2;
                    } else {
                        var competitor = $scope.challenge.user1;
                    }

                    $scope.count_down_timer = 10; // 30 sec

                    $scope.messages = [];

                    $scope.messages.push('The game connection is processing step 5');

                    if ($scope.challenge.user1.id == $rootScope.my_info.id) {
                        startGame('xEstablishMPGame');
                    } else {
                        startGame('xEstablishMPGameReceive');
                    }

                    var waitingForxRecievedJson = function () {
                        $scope.count_down_timer -= 1;

                        if (!response_received) {
                            log.debug('Waiting for xRecievedJson from Unity...');
                            $scope.messages.push($scope.count_down_timer + '...');

                        }

                        if ($scope.count_down_timer < 1) {
                            $scope.messages.push('failed');
                            log.debug('count down timer < 1 in onconnecting_to_unity');
                            $scope.fsm.cant_play();
                        }
                    }

                    timer_unity = $interval(waitingForxRecievedJson, 3000);


                    $scope.xRecievedJson = function () {
                        log.debug('Response from UNITY - xRecievedJson');
                        response_received = true;
                        $scope.messages.push('ok');

                        if ($scope.challenge.user1.id == $rootScope.my_info.id) {
                            $scope.challenge.user1.connected_to_unity = true;
                        } else {
                            $scope.challenge.user2.connected_to_unity = true;
                        }

                        socket.emit('user_message', {'action': 'user_connected_to_unity', 'data': {'from': $rootScope.my_info, 'to': competitor, 'challenge': $scope.challenge}, 'room': room})

                        if ($scope.challenge.user1.connected_to_unity &&
                            $scope.challenge.user2.connected_to_unity) {
                            $interval.cancel(timer_unity);
                            $scope.fsm.connected_to_unity();
                        } else {
                            $scope.messages.push('Waiting for opponent...');
                        }
                    }

                    socket.socket.removeListener('msg_to_room');
                    socket.on('msg_to_room', function (msg) {
                        log.debug('4 on msg_to_room: ' + angular.toJson(msg))

                        if (msg.action == 'user_connected_to_unity' && msg.data.to.id == $rootScope.my_info.id) {
                            log.debug('Its for me');
                            if (msg.data.challenge.user1.id == msg.data.from.id) {
                                log.debug('user1 connected to unity');
                                $scope.challenge.user1.connected_to_unity = true;
                            } else if (msg.data.challenge.user2.id == msg.data.from.id) {
                                log.debug('user2 connected to unity');
                                $scope.challenge.user2.connected_to_unity = true;
                            }

                            if ($scope.challenge.user1.connected_to_unity &&
                                $scope.challenge.user2.connected_to_unity) {
                                $interval.cancel(timer_unity);
                                log.debug('all users are connected to unity');
                                $scope.fsm.connected_to_unity();
                            }
                        } else if (msg.action == 'challenge_cancel' && msg.data.to.id == $rootScope.my_info.id) {
                            $scope.fsm.reset();
                        }

                    });

                    $scope.cancelChallenge = function () {

                        socket.emit('user_message', {'action': 'challenge_cancel', 'data': {'from': $rootScope.my_info, 'to': getCompetitor(), 'challenge': $scope.challenge}, 'room': room});
                        $scope.fsm.reset();
                    }


                },
                // ===========================================================
                onleaveconnecting_to_unity: function () {
                    $interval.cancel(timer_unity);
                    log.info('LEAVE ')

                },
                // ===========================================================
                onfailed: function () {
                    $scope.cancelChallenge = function () {
                        socket.emit('user_message', {'action': 'challenge_cancel', 'data': $scope.challenge, 'room': room});
                        $scope.fsm.reset();
                    }

                },
                // ===========================================================
                onconnecting: function () {
                    log.info('onconnecting');

                    $scope.messages = []

                    if (selected_mode == 'lan') {

                    } else if (selected_mode == 'bluetooth') {

                    } else if (selected_mode == 'server') {

                    }


                    $scope.count_down_timer = 50;

                    log.debug('!!!!! Waiting for connect... (' + selected_mode + ')');
                    $scope.messages.push('Waiting for connect... (' + selected_mode + ')')

                    var waitingForConnect = function () {
                        log.debug('WAITING FOR TIMER...')
                        $scope.count_down_timer -= 1;

                        if ($scope.challenge.server && $scope.challenge.client) {
                            log.debug('# waiting for if ($scope.challenge.server && $scope.challenge.client) ..')
                            log.debug(angular.toJson($scope.challenge))
                            log.debug('#')
                            if ($scope.challenge.server.result.toLowerCase() == 'success' && $scope.challenge.client.result.toLowerCase() == 'success') {
                                $interval.cancel(timer);
                                $scope.fsm.startgame()
                            }
                        }

                        //console.error($scope.challenge);


                        $scope.messages[$scope.messages.length - 1] = $scope.messages[$scope.messages.length - 1] + '.';


                        if ($scope.count_down_timer < 1) {
                            $scope.messages.push('failed');
                            log.debug('count down timer < 1 in onconnecting');
                            $interval.cancel(timer);
                            $scope.fsm.cant_play();
                        }
                    }

                    timer = $interval(waitingForConnect, 3000);

                    $scope.cancelChallenge = function () {
                        socket.emit('user_message', {'action': 'challenge_cancel', 'data': {'from': $rootScope.my_info, 'to': getCompetitor(), 'challenge': $scope.challenge}, 'room': room});
                        $scope.fsm.reset();
                    }

                    socket.socket.removeListener('msg_to_room');
                    socket.on('msg_to_room', function (msg) {
                        log.debug('4 on msg_to_room: ' + angular.toJson(msg))
                        if (msg.action == 'challenge_cancel' && msg.data.to.id == $rootScope.my_info.id) {
                            $scope.fsm.reset();
                        }
                    });
                },

                // ===========================================================
                onstarting: function () {
                    log.debug('### Start game... on starting');

                    log.debug('A debug info about my rootScope and scope.challenge')
                    log.debug(angular.toJson($rootScope.my_info));
                    log.debug(angular.toJson($scope.challenge));

                    var data = {
                        'player1': $scope.challenge.user1.id,
                        'player2': $scope.challenge.user2.id,
                        'challenge_guid': $scope.challenge.guid,
                        'gumballs': $scope.challenge.gumballs
                    }

                    log.debug('Game id is '+$rootScope.my_info.game_id)
                    log.debug(angular.toJson(data));

                    log.debug('try to save')

                    MatchServiceMP.save({'game_id': $rootScope.my_info.game_id}, data, function (data) {
                        $scope.fsm.play();
                    },function (data) {
                        $scope.fsm.play();
                    });
                },
                // ===========================================================
                onplaying: function () {


                    $scope.xPause = function () {
                        log.debug('Response from UNITY - xPause');

                        if ($scope.challenge.user1.id == $rootScope.my_info.id) {
                            var competitor = $scope.challenge.user2;
                        } else {
                            var competitor = $scope.challenge.user1;
                        }

                        socket.emit('user_message', {'action': 'pause', 'data': {'from': $rootScope.my_info, 'to': competitor, 'challenge': $scope.challenge}, 'room': room});

                        $scope.fsm.pause();
                    }

                    socket.socket.removeListener('msg_to_room');
                    socket.on('msg_to_room', function (msg) {
                        log.debug('on msg_to_room: ' + angular.toJson(msg))
                        if (msg.action == 'pause' && msg.data.to.id == $rootScope.my_info.id) {
                            $scope.fsm.wait_pause();
                        }
                    });
                },
                // ===========================================================
                onpausing: function () {


                    $scope.xResume = function () {
                        log.debug('Response from UNITY - xResume');

                        if ($scope.challenge.user1.id == $rootScope.my_info.id) {
                            var competitor = $scope.challenge.user2;
                        } else {
                            var competitor = $scope.challenge.user1;
                        }

                        socket.emit('user_message', {'action': 'resume', 'data': {'from': $rootScope.my_info, 'to': competitor, 'challenge': $scope.challenge}, 'room': room});

                        $scope.fsm.play();
                    }

                    $scope.resumeChallenge = function () {
                        $scope.xResume();
                    }

                    $scope.cancelChallenge = function () {
                        socket.emit('user_message', {'action': 'challenge_cancel', 'data': {'from': $rootScope.my_info, 'to': getCompetitor(), 'challenge': $scope.challenge}, 'room': room});
                        $scope.fsm.quit();
                    }


                    socket.socket.removeListener('msg_to_room');
                    socket.on('msg_to_room', function (msg) {
                        log.debug('on msg_to_room: ' + angular.toJson(msg))
                        if (msg.action == 'challenge_cancel' && msg.data.to.id == $rootScope.my_info.id) {
                            $scope.fsm.quit();
                        }
                    });


                },
                // ===========================================================
                onready_pause: function () {
                    socket.socket.removeListener('msg_to_room');
                    socket.on('msg_to_room', function (msg) {
                        log.debug('on msg_to_room: ' + angular.toJson(msg))
                        if (msg.action == 'resume' && msg.data.to.id == $rootScope.my_info.id) {
                            $scope.fsm.play();
                        } else if (msg.action == 'challenge_cancel' && msg.data.to.id == $rootScope.my_info.id) {
                            $scope.fsm.quit();
                        }
                    });

                    $scope.cancelChallenge = function () {
                        socket.emit('user_message', {'action': 'challenge_cancel', 'data': {'from': $rootScope.my_info, 'to': getCompetitor(), 'challenge': $scope.challenge}, 'room': room});
                        $scope.fsm.quit();
                    }

                },

                // ===========================================================
                onquitting: function () {
                    $scope.mainScreen = function () {
                        log.debug('main screen');
                        $scope.fsm.reset();
                    }

                }



            }
        });
    }

    socket.socket.removeListener('system_msg_to_room');

    socket.on('system_msg_to_room', function (msg) {

        log.warn('on sys_msg_to_room: ' + angular.toJson(msg));

        if (msg.action == 'update_client_info') {
            if (msg.challenge == $scope.challenge.guid) {
                log.warn('CLIENT INFO: update client info')
                $scope.challenge.client = msg.response;
                $scope.challenge.mode = msg.response.type;
                log.warn('call xClientReady')
                engine.call('xClientReady', angular.toJson($scope.challenge));
            }
        } else if (msg.action == 'update_server_info') {
            if (msg.challenge == $scope.challenge.guid) {
                log.warn('SERVER INFO: update server info')
                $scope.challenge.server = msg.response;
                $scope.challenge.mode = msg.response.type;
                log.warn('call xServerReady')
                engine.call('xServerReady', angular.toJson($scope.challenge));
            }
        }


    });


    // UNITY -----------------------------------------------------------------

    $scope.xSetServerStatus = function (data) {
        data = angular.fromJson(data)
        log.debug('Response from UNITY xSetServerStatus... ' + angular.toJson(data));

        if (data.challenge == $scope.challenge.guid) {
            log.warn('MY')
            $scope.challenge.server = data;
            $scope.challenge.mode = data.type;
        }

        socket.emit('system_message', {'action': 'update_server_info', 'challenge': data.challenge, 'response': data, 'room': room})
    }

    $scope.xSetClientStatus = function (data) {
        data = angular.fromJson(data)
        log.debug('Response from UNITY xSetClientStatus... ' + angular.toJson(data));

        if (data.challenge == $scope.challenge.guid) {
            log.warn('MY')
            $scope.challenge.client = data;
            $scope.challenge.mode = data.type;
        }

        socket.emit('system_message', {'action': 'update_client_info', 'challenge': data.challenge, 'response': data, 'room': room})
    }


    $scope.xSetMyLocalIP = function (data) {
        // called by unity
        log.debug('Response from UNITY with local ip...');
        log.debug(data);

        var answer = angular.fromJson(data);

        $rootScope.$apply(function () {
            $rootScope.my_info['local_ip'] = answer['local_ip'];
            $rootScope.my_info['local_port'] = answer['local_port'];

            socket.emit('update_my_info', $rootScope.my_info);
            log.debug('Updated...');
        });

        return true;
    }

    $scope.xSetMyBluetoothInfo = function (data) {
        // called by unity
        log.debug('Response from UNITY with bluetooth info...');
        log.debug(data);

        var answer = angular.fromJson(data);

        $rootScope.$apply(function () {
            $rootScope.my_info['bluetooth_name'] = answer['name'];
            $rootScope.my_info['bluetooth_nearby_devices'] = answer['nearby_devices'];

            socket.emit('update_my_info', $rootScope.my_info);
            log.debug('Updated...');
        });

        return true;
    }


    $scope.xSetMyConnectionType = function (match_id, player_id, connection_type) {
        log.debug('Response from UNITY xSetMyConnectionType... ' + match_id + ', ' + player_id + ', ' + connection_type);
    }

    $scope.xSetMyStatus = function (match_id, player_id, status) {
        log.debug('Response from UNITY xSetMyStatus... ' + match_id + ', ' + player_id + ', ' + status);
    }

    $scope.xSetConfirmedConnection = function (match_id, dt) {
        log.debug('Response from UNITY xSetConfirmedConnection... ' + match_id + ', ' + dt);
    }

    $scope.xSetScore = function (match_id, player_id, score) {
        log.debug('Response from UNITY xSetScore... ' + match_id + ', ' + player_id + ', ' + score);
    }

    // UNITY -----------------------------------------------------------------


    // TEST

    $scope.xTestFromPlay = function () {
        log.debug('test')


        $scope.fsm.startgame();
    }

    //

    $scope.$on('$destroy', function (event) {
        log.debug('leave room');
        $scope.fsm.reset();
        socket.emit('unsubscribe', {'user': $rootScope.my_info, 'room': room, 'user_id': $rootScope.my_info.id});
        socket.socket.removeListener('msg_to_room');
        socket.socket.removeListener('update_users');


    });


    // ----------------------------------------------------------------------------
    // SOCKET EVENTS
    // ----------------------------------------------------------------------------

    socket.on('connect', function (data) {
        log.debug('on connect')
    });

    socket.on('info', function (message) {
        log.debug('on info: ' + message);
    });

    socket.on('announcement', function (msg) {
        log.debug('on announcement: ' + angular.toJson(msg))
    });


    // ----------------------------------------------------------------------------


    var startGame = function (method_name) {
        log.debug('startGame');
        var game = CurrentGameService.get(function () {
            var servers = $filter('orderBy')(game.servers, 'avg_load');

            if (!servers) {
                alert('no servers');
            }

            var server = servers[0];

            if (!$rootScope.my_info.local_port) {
                $rootScope.my_info.local_port = 80;
            }

            if (!$rootScope.my_info.local_ip) {
                $rootScope.my_info.local_ip = null;
            }

            if (!$scope.match_id) {
                $scope.match_id = null
            }

            // nearst server
            if ($scope.challenge.nearest_server) {
                game.servers.splice(0, 0, $scope.challenge.nearest_server);
            }

            var data = angular.toJson({
                'my_info': $rootScope.my_info,
                'challenge': {
                    'match_id': $scope.match_id,
                    'guid': $scope.challenge.guid,
                    'my_state': $scope.fsm.current,
                    'users': [ $scope.challenge.user1, $scope.challenge.user2 ]
                },
                'game_info': game
            });

            log.debug('Starting the Game... method ' + method_name);
            log.debug(data.toString());
            engine.call(method_name, data.toString());
            log.debug('Done.');

        });
    }

}]);
