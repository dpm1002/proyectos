using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Runtime.InteropServices;

namespace TecladoUniversal
{
    public partial class UserControl1: UserControl
    {
        public UserControl1()
        {
            InitializeComponent();
            CargarTecladosInstalados();

            
        }

        private static readonly Dictionary<string, string> LayoutIdMapping = new Dictionary<string, string>
        {
            { "Japonés", "00000411" },
            { "Coreano", "00000412" },
            { "Español", "0000040A" },
            { "Inglés (Estados Unidos)", "00000409" },
            { "Francés", "0000040C" },
        };

        private void CargarTecladosInstalados()
        {
            comboBox1.Items.Clear();

            // Utiliza un HashSet para evitar duplicados
            HashSet<string> seenLayouts = new HashSet<string>();

            foreach (InputLanguage lang in InputLanguage.InstalledInputLanguages)
            {
                // Obtén el Layout ID en formato hexadecimal
                string layoutIdHex = lang.Culture.KeyboardLayoutId.ToString("X").PadLeft(8, '0');

                // Asegúrate de que tenga al menos 8 caracteres
                if (layoutIdHex.Length > 8)
                {
                    layoutIdHex = layoutIdHex.Substring(layoutIdHex.Length - 8);
                }

                // Solo agrega si el Layout ID no está ya en el HashSet
                if (!seenLayouts.Contains(layoutIdHex))
                {
                    seenLayouts.Add(layoutIdHex);
                    comboBox1.Items.Add(new ComboBoxItem(lang.LayoutName, layoutIdHex));
                }
            }
        }






        public static class KeyboardLayoutChanger {

            // Importa la función LoadKeyboardLayout de user32.dll
            [DllImport("user32.dll", CharSet = CharSet.Auto)]
            public static extern IntPtr LoadKeyboardLayout(string pwszKLID, uint Flags);

            // Define una constante para activar el layout
            public const uint KLF_ACTIVATE = 0x00000001;

            // Método para cambiar el layout del teclado según el código
            public static void SetKeyboardLayout(string layoutCode)
            {
                LoadKeyboardLayout(layoutCode, KLF_ACTIVATE);
            }

        }

        private void comboBox1_SelectedIndexChanged(object sender, EventArgs e)
        {

            if (comboBox1.SelectedItem is ComboBoxItem selectedItem)
            {
                string layoutCode = selectedItem.Value;
                Console.WriteLine($"Cambiando teclado a {layoutCode}");
                label1.Text = selectedItem.Text;

                // Cambiar el teclado
                KeyboardLayoutChanger.SetKeyboardLayout(layoutCode);
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            Clipboard.Clear();
            if (textBox1.Text == "") {
                
            }
            else {
                Clipboard.SetText(textBox1.Text);
            }
            

        }

        public class ComboBoxItem
        {
            public string Text { get; set; }
            public string Value { get; set; }

            public ComboBoxItem(string text, string value)
            {
                Text = text;
                Value = value;
            }

            public override string ToString()
            {
                return Text;
            }
        }


    }
}
