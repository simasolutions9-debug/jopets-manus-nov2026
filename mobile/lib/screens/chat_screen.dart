import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/io.dart';
import '../api.dart';

const _navy = Color(0xFF123B73);
const _teal = Color(0xFF26A69A);

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key, this.tenantId, this.peerId});
  final String? tenantId;
  final String? peerId;
  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _api = JopetsApi();
  final _input = TextEditingController();
  final _messages = <Map<String, dynamic>>[];
  StreamSubscription? _subscription;
  IOWebSocketChannel? _channel;
  String? _userId;
  String? _error;
  bool _connected = false;

  @override
  void initState() { super.initState(); _connect(); }
  @override
  void dispose() { _subscription?.cancel(); _channel?.sink.close(); _input.dispose(); super.dispose(); }

  Future<void> _connect() async {
    final tenant = widget.tenantId ?? const String.fromEnvironment('JOPETS_TENANT_ID');
    final peer = widget.peerId ?? const String.fromEnvironment('JOPETS_CHAT_PEER_ID');
    final token = await _api.accessTokenValue();
    _userId = await _api.userIdValue();
    if (tenant.isEmpty || peer.isEmpty || token == null || token.isEmpty) { if (mounted) setState(() => _error = 'Configura sesión, tenant y proveedor para iniciar el chat.'); return; }
    try {
      final url = _api.websocketChatUrl(tenantId: tenant, peerId: peer);
      final channel = IOWebSocketChannel.connect(Uri.parse(url), headers: {'Authorization': 'Bearer $token'});
      _channel = channel;
      _subscription = channel.stream.listen((raw) { final data = jsonDecode(raw.toString()); if (data['type'] == 'message' && mounted) setState(() => _messages.add(data as Map<String, dynamic>)); }, onError: (_) => _fail('No se pudo mantener la conexión.'), onDone: () => _fail('La conexión fue cerrada.'));
      if (mounted) setState(() { _connected = true; _error = null; });
    } catch (_) { _fail('No se pudo conectar al chat en tiempo real.'); }
  }

  void _fail(String message) { if (mounted) setState(() { _connected = false; _error = message; }); }
  void _send() { final text = _input.text.trim(); if (text.isEmpty || !_connected) return; _channel?.sink.add(jsonEncode({'text': text})); _input.clear(); }

  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(backgroundColor: _navy, foregroundColor: Colors.white, title: const Text('Chat seguro')), body: Column(children: [if (_error != null) Padding(padding: const EdgeInsets.all(12), child: Text(_error!, style: const TextStyle(color: Colors.red))), Expanded(child: _messages.isEmpty ? const Center(child: Text('No hay mensajes todavía.')) : ListView.builder(itemCount: _messages.length, itemBuilder: (context, index) { final message = _messages[index]; final mine = _userId != null && message['sender_id'].toString() == _userId; return Align(alignment: mine ? Alignment.centerRight : Alignment.centerLeft, child: Card(color: mine ? _teal : Colors.white, child: Padding(padding: const EdgeInsets.all(12), child: Text(message['text']?.toString() ?? '')))); })), SafeArea(child: Row(children: [Expanded(child: TextField(controller: _input, enabled: _connected, onSubmitted: (_) => _send(), decoration: const InputDecoration(hintText: 'Escribe un mensaje'))), IconButton(onPressed: _connected ? _send : null, icon: const Icon(Icons.send, color: _teal))]))]));
}
