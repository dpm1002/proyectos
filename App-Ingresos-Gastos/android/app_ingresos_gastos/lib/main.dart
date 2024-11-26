import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Gestión de Ingresos y Gastos',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _selectedIndex = 0;

  final List<Widget> _pages = [
    AddTransactionPage(),
    TransactionsPage(),
    GraphsPage(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Gestión de Ingresos y Gastos'),
      ),
      body: _pages[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.add),
            label: 'Añadir',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.list),
            label: 'Ver Transacciones',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.bar_chart),
            label: 'Gráficas',
          ),
        ],
        currentIndex: _selectedIndex,
        selectedItemColor: Colors.blue,
        onTap: _onItemTapped,
      ),
    );
  }
}

class AddTransactionPage extends StatelessWidget {
  final TextEditingController _descriptionController = TextEditingController();
  final TextEditingController _amountController = TextEditingController();

  Future<void> _addTransaction(String type) async {
    await FirebaseFirestore.instance
        .collection(type == 'income' ? 'incomes' : 'expenses')
        .add({
      'description': _descriptionController.text,
      'amount': double.parse(_amountController.text),
      'type': type,
      'timestamp': FieldValue.serverTimestamp(),
    });
    print('$type añadido correctamente');
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          TextField(
            controller: _descriptionController,
            decoration: InputDecoration(labelText: 'Descripción'),
          ),
          TextField(
            controller: _amountController,
            decoration: InputDecoration(labelText: 'Cantidad'),
            keyboardType: TextInputType.number,
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              ElevatedButton(
                onPressed: () => _addTransaction('income'),
                child: Text('Añadir Ingreso'),
              ),
              ElevatedButton(
                onPressed: () => _addTransaction('expense'),
                child: Text('Añadir Gasto'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class TransactionsPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return StreamBuilder<QuerySnapshot>(
      stream: FirebaseFirestore.instance
          .collectionGroup('transactions')
          .snapshots(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Center(child: CircularProgressIndicator());
        } else if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        } else if (!snapshot.hasData || snapshot.data!.docs.isEmpty) {
          return Center(child: Text('No hay transacciones registradas'));
        } else {
          final transactions = snapshot.data!.docs;
          return ListView.builder(
            itemCount: transactions.length,
            itemBuilder: (context, index) {
              final transaction = transactions[index];
              final data = transaction.data() as Map<String, dynamic>;
              return ListTile(
                title: Text(data['description']),
                subtitle: Text('${data['type']} - ${data['amount']}'),
                trailing: IconButton(
                  icon: Icon(Icons.delete),
                  onPressed: () async {
                    await transaction.reference.delete();
                    print('Transacción eliminada');
                  },
                ),
              );
            },
          );
        }
      },
    );
  }
}

class GraphsPage extends StatelessWidget {
  Future<Map<String, double>> _fetchGraphData(String collection) async {
    final snapshot =
        await FirebaseFirestore.instance.collection(collection).get();
    Map<String, double> data = {};
    for (var doc in snapshot.docs) {
      final description = doc['description'];
      final amount = doc['amount'];
      data[description] = (data[description] ?? 0) + amount;
    }
    return data;
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map<String, double>>(
      future: _fetchGraphData('expenses'), // Cambiar a 'incomes' para ingresos
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Center(child: CircularProgressIndicator());
        } else if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
          return Center(child: Text('No hay datos para mostrar'));
        } else {
          final data = snapshot.data!;
          return ListView(
            children: data.entries.map((entry) {
              return ListTile(
                title: Text(entry.key),
                trailing: Text(entry.value.toStringAsFixed(2)),
              );
            }).toList(),
          );
        }
      },
    );
  }
}
