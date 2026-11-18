import 'dart:convert';
import 'dart:io';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class ApiConfig {
  static const baseUrl = String.fromEnvironment('API_BASE_URL');
  static const tenantId = String.fromEnvironment('JOPETS_TENANT_ID');
}

class JopetsApi {
  JopetsApi({String? baseUrl, this.client, this.tenantId, this.accessToken, FlutterSecureStorage? storage}) : baseUrl = (baseUrl ?? ApiConfig.baseUrl).replaceAll(RegExp(r'/$'), ''), _storage = storage ?? const FlutterSecureStorage();
  final String baseUrl;
  final http.Client? client;
  final String? tenantId;
  final String? accessToken;
  final FlutterSecureStorage _storage;
  http.Client get _http => client ?? http.Client();

  Future<Map<String, String>> _headers({bool json = false}) async {
    final token = accessToken ?? await _storage.read(key: 'jopets_access_token');
    final tenant = tenantId ?? await _storage.read(key: 'jopets_tenant_id') ?? ApiConfig.tenantId;
    return {'Accept': 'application/json', if (json) 'Content-Type': 'application/json', if (tenant.isNotEmpty) 'X-Tenant-ID': tenant, if (token != null && token.isNotEmpty) 'Authorization': 'Bearer $token'};
  }
  Future<http.Response> _request(Future<http.Response> Function() request) async {
    if (baseUrl.isEmpty) throw const ApiException(0, 'API_BASE_URL no está configurada');
    try { return await request(); } on SocketException { throw const ApiException(0, 'Error de conexión al servidor'); } on http.ClientException { throw const ApiException(0, 'Error de conexión al servidor'); }
  }
  dynamic _json(http.Response response) => response.body.isEmpty ? <String, dynamic>{} : jsonDecode(response.body);
  Map<String, dynamic> _object(http.Response response) { final data = _json(response); if (response.statusCode < 200 || response.statusCode >= 300) throw ApiException(response.statusCode, data is Map ? data['detail']?.toString() ?? 'La solicitud no pudo completarse' : 'La solicitud no pudo completarse'); if (data is! Map) throw const ApiException(500, 'Respuesta inválida del servidor'); return Map<String, dynamic>.from(data); }
  List<Map<String, dynamic>> _list(http.Response response) { final data = _json(response); if (response.statusCode < 200 || response.statusCode >= 300) throw ApiException(response.statusCode, data is Map ? data['detail']?.toString() ?? 'La solicitud no pudo completarse' : 'La solicitud no pudo completarse'); if (data is! List) throw const ApiException(500, 'Respuesta de lista inválida'); return data.whereType<Map>().map((row) => Map<String, dynamic>.from(row)).toList(); }

  Future<LoginSession> login({required String email, required String password, String? totpCode}) async { final response = await _request(() => _http.post(Uri.parse('$baseUrl/api/auth/token'), headers: _headersSync(json: true), body: jsonEncode({'username': email, 'password': password, if (totpCode != null && totpCode.isNotEmpty) 'totp_code': totpCode}))); final session = LoginSession.fromJson(_object(response)); await _storage.write(key: 'jopets_access_token', value: session.accessToken); await _storage.write(key: 'jopets_refresh_token', value: session.refreshToken); if (session.role != null) await _storage.write(key: 'jopets_role', value: session.role); if (session.userId != null) await _storage.write(key: 'jopets_user_id', value: session.userId); if (session.tenantId != null) await _storage.write(key: 'jopets_tenant_id', value: session.tenantId); return session; }
  Map<String, String> _headersSync({bool json = false}) => {'Accept': 'application/json', if (json) 'Content-Type': 'application/json', if (tenantId != null && tenantId!.isNotEmpty) 'X-Tenant-ID': tenantId!, if (accessToken != null && accessToken!.isNotEmpty) 'Authorization': 'Bearer $accessToken'};
  Future<Map<String, dynamic>> register({required String name, required String email, required String city, required String password}) async { final response = await _request(() => _http.post(Uri.parse('$baseUrl/api/auth/register'), headers: _headersSync(json: true), body: jsonEncode({'name': name, 'email': email, 'city': city, 'password': password}))); return _object(response); }
  Future<void> logout() async { await _storage.deleteAll(); }
  Future<bool> hasStoredSession() async => (await _storage.read(key: 'jopets_access_token'))?.isNotEmpty == true;
  Future<String?> role() => _storage.read(key: 'jopets_role');
  Future<String?> accessTokenValue() => accessToken != null ? Future.value(accessToken) : _storage.read(key: 'jopets_access_token');
  Future<String?> userIdValue() => _storage.read(key: 'jopets_user_id');
  Future<String?> tenantIdValue() => _storage.read(key: 'jopets_tenant_id');
  Future<List<Map<String, dynamic>>> pets() async { final response = await _request(() async => _http.get(Uri.parse('$baseUrl/api/client/pets'), headers: await _headers())); return _list(response); }
  Future<List<Map<String, dynamic>>> bookings() async { final response = await _request(() async => _http.get(Uri.parse('$baseUrl/api/client/bookings'), headers: await _headers())); return _list(response); }
  Future<List<Map<String, dynamic>>> marketplaceProducts() async { final response = await _request(() async => _http.get(Uri.parse('$baseUrl/api/marketplace/products'), headers: await _headers())); return _list(response); }
  Future<Map<String, dynamic>> marketplaceProduct(String productId) async { final products = await marketplaceProducts(); for (final item in products) { if (item['id']?.toString() == productId) return item; } throw const ApiException(404, 'Producto no encontrado en el servidor'); }
  Future<Map<String, dynamic>> createBooking(String petId, Map<String, dynamic> priceSnapshot, {String? providerId}) async { final response = await _request(() async => _http.post(Uri.parse('$baseUrl/api/client/bookings'), headers: await _headers(json: true), body: jsonEncode({'pet_id': petId, 'price_snapshot': priceSnapshot, if (providerId != null) 'provider_id': providerId}))); return _object(response); }
  Future<String> petQr(String petId) async { final response = await _request(() async => _http.get(Uri.parse('$baseUrl/api/client/pets/$petId/qr'), headers: await _headers())); final qr = _object(response)['pet_qr']; if (qr is! String || qr.isEmpty) throw const ApiException(500, 'El servidor no devolvió el código QR'); return qr; }
  Future<Map<String, dynamic>> updatePet(String petId, Map<String, dynamic> data) async { final response = await _request(() async => _http.patch(Uri.parse('$baseUrl/api/client/pets/$petId'), headers: await _headers(json: true), body: jsonEncode(data))); return _object(response); }
  Future<Map<String, dynamic>> medicalHistory(String petId) async { final response = await _request(() async => _http.get(Uri.parse('$baseUrl/api/client/pets/$petId/medical-history'), headers: await _headers())); return _object(response); }
  Future<List<Map<String, dynamic>>> vaccines(String petId) async { final response = await _request(() async => _http.get(Uri.parse('$baseUrl/api/client/pets/$petId/vaccines'), headers: await _headers())); return _list(response); }
  Future<List<Map<String, dynamic>>> notifications() async { final response = await _request(() async => _http.get(Uri.parse('$baseUrl/api/client/notifications'), headers: await _headers())); return _list(response); }
  Future<Map<String, dynamic>> providerWallet() async { final response = await _request(() async => _http.get(Uri.parse('$baseUrl/api/provider/wallet'), headers: await _headers())); return _object(response); }
  Future<List<Map<String, dynamic>>> providerAgenda() async { final response = await _request(() async => _http.get(Uri.parse('$baseUrl/api/provider/bookings'), headers: await _headers())); return _list(response); }
  String websocketChatUrl({required String tenantId, required String peerId}) { final parsed = Uri.parse(baseUrl); return Uri(scheme: parsed.scheme == 'https' ? 'wss' : 'ws', host: parsed.host, port: parsed.hasPort ? parsed.port : null, path: '/ws/chat/$tenantId/$peerId/').toString(); }
}

class LoginSession { const LoginSession({required this.accessToken, required this.refreshToken, this.role, this.tenantId, this.userId}); final String accessToken; final String refreshToken; final String? role; final String? tenantId; final String? userId; factory LoginSession.fromJson(Map<String, dynamic> json) => LoginSession(accessToken: json['access'] as String, refreshToken: json['refresh'] as String, role: json['role'] as String?, tenantId: json['tenant_id']?.toString(), userId: json['user_id']?.toString()); }
class ApiException implements Exception { const ApiException(this.statusCode, this.message); final int statusCode; final String message; @override String toString() => message; }
