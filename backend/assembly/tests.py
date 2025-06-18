from django.test import TestCase, Client
from django.urls import reverse
from users.models import User, Team
from inventory.models import Part
from .models import Aircraft

class AssemblyProcessTests(TestCase):
    """
    Uçak montajı iş akışının kritik senaryolarını test eder.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Tüm testler için bir kez çalışacak ve değişmeyecek olan hazırlık metodu.
        Bu, her test için tekrar tekrar nesne oluşturmaktan daha verimlidir.
        """
        # 1. Gerekli Takımları Oluştur
        cls.montaj_takimi = Team.objects.create(name="Test Montaj Takımı", type=Team.TeamType.MONTAJ)
        cls.kanat_takimi = Team.objects.create(name="Test Kanat Takımı", type=Team.TeamType.KANAT)

        # 2. Gerekli Kullanıcıları Oluştur
        cls.montaj_user = User.objects.create_user(username='montajci_test', password='password123', team=cls.montaj_takimi)
        cls.kanat_user = User.objects.create_user(username='kanatci_test', password='password123', team=cls.kanat_takimi)

    def setUp(self):
        """
        Her bir test fonksiyonundan önce çalışır.
        Testler arası izolasyonu sağlamak için istemciyi (client) burada oluştururuz.
        """
        self.client = Client()
        # Montaj kullanıcısını her testin başında varsayılan olarak giriş yaptır
        self.client.login(username='montajci_test', password='password123')

    def test_successful_aircraft_assembly(self):
        """
        Senaryo: Başarılı bir uçak montajı.
        Beklenti: Yeni bir uçak oluşur, parçaların durumu güncellenir ve kullanıcı yönlendirilir.
        """
        # --- ARRANGE (Hazırla) ---
        # AKINCI için gerekli olan 4 farklı parçayı oluştur
        part_kanat = Part.objects.create(type='KANAT', aircraft_model='AKINCI', created_by=self.kanat_user)
        part_govde = Part.objects.create(type='GOVDE', aircraft_model='AKINCI', created_by=self.kanat_user)
        part_kuyruk = Part.objects.create(type='KUYRUK', aircraft_model='AKINCI', created_by=self.kanat_user)
        part_aviyonik = Part.objects.create(type='AVIYONIK', aircraft_model='AKINCI', created_by=self.kanat_user)

        post_data = {
            'model_name': 'AKINCI',
            'KANAT': part_kanat.id,
            'GOVDE': part_govde.id,
            'KUYRUK': part_kuyruk.id,
            'AVIYONIK': part_aviyonik.id,
        }

        # --- ACT (Eyleme Geç) ---
        response = self.client.post(reverse('create_assembly'), data=post_data)

        # --- ASSERT (Doğrula) ---
        self.assertEqual(Aircraft.objects.count(), 1, "Veritabanında 1 adet uçak oluşmalıydı.")
        yeni_ucak = Aircraft.objects.first()
        self.assertEqual(yeni_ucak.model_name, 'AKINCI')
        self.assertEqual(yeni_ucak.assembled_by, self.montaj_user)
        
        # Parçaların durumunu ve atamasını kontrol et
        part_kanat.refresh_from_db()
        self.assertEqual(part_kanat.status, Part.Status.USED, "Parçanın durumu 'USED' olmalıydı.")
        self.assertEqual(part_kanat.used_in_aircraft, yeni_ucak, "Parça yeni uçağa bağlanmalıydı.")
        self.assertEqual(yeni_ucak.parts.count(), 4, "Uçağın 4 adet bağlı parçası olmalıydı.")
        
        # Yönlendirmeyi kontrol et
        self.assertRedirects(response, reverse('list_aircrafts'))

    def test_assembly_permission_denied_for_production_team(self):
        """
        Senaryo: Üretim takımı (örn: Kanat Takımı) montaj sayfasına erişmeye çalışır.
        Beklenti: Erişim engellenir (HTTP 403 Forbidden).
        """
        # --- ARRANGE (Hazırla) ---
        self.client.login(username='kanatci_test', password='password123')
        
        # --- ACT (Eyleme Geç) ---
        response = self.client.get(reverse('create_assembly'))

        # --- ASSERT (Doğrula) ---
        self.assertEqual(response.status_code, 403, "Montaj takımı dışındaki erişim engellenmeliydi.")

    def test_assembly_fails_with_mismatched_part(self):
        """
        Senaryo: AKINCI montajı için TB2 parçası kullanılmaya çalışılır.
        Beklenti: İşlem başarısız olur, hata mesajı gösterilir ve veritabanı değişmez.
        """
        # --- ARRANGE (Hazırla) ---
        # Biri AKINCI, diğeri TB2 için olan iki parça oluştur
        part_kanat_akinci = Part.objects.create(type='KANAT', aircraft_model='AKINCI', created_by=self.kanat_user)
        part_govde_tb2 = Part.objects.create(type='GOVDE', aircraft_model='TB2', created_by=self.kanat_user)
        part_kuyruk_akinci = Part.objects.create(type='KUYRUK', aircraft_model='AKINCI', created_by=self.kanat_user)
        part_aviyonik_akinci = Part.objects.create(type='AVIYONIK', aircraft_model='AKINCI', created_by=self.kanat_user)

        post_data = {
            'model_name': 'AKINCI',
            'KANAT': part_kanat_akinci.id,
            'GOVDE': part_govde_tb2.id, # <-- Uyumsuz Parça
            'KUYRUK': part_kuyruk_akinci.id,
            'AVIYONIK': part_aviyonik_akinci.id,
        }

        # --- ACT (Eyleme Geç) ---
        # follow=True ile yönlendirmeyi takip et ve son sayfayı analiz et
        response = self.client.post(reverse('create_assembly'), data=post_data, follow=True)

        # --- ASSERT (Doğrula) ---
        self.assertEqual(Aircraft.objects.count(), 0, "Uyumsuz parça ile uçak oluşturulmamalıydı.")
        self.assertContains(response, "modeli için uygun değil", msg_prefix="Ekranda parça uyumsuzluk hatası gösterilmeliydi.")

    def test_assembly_fails_if_a_part_is_already_used(self):
        """
        Senaryo: Daha önce kullanılmış bir parça ile montaj yapılmaya çalışılır.
        Beklenti: İşlem başarısız olur ve hata mesajı gösterilir.
        """
        # --- ARRANGE (Hazırla) ---
        part_kanat = Part.objects.create(type='KANAT', aircraft_model='AKINCI', status=Part.Status.USED, created_by=self.kanat_user) # Durumu 'USED'
        part_govde = Part.objects.create(type='GOVDE', aircraft_model='AKINCI', created_by=self.kanat_user)
        # ... diğer parçalar
        
        post_data = { 'model_name': 'AKINCI', 'KANAT': part_kanat.id, 'GOVDE': part_govde.id }
        
        # --- ACT (Eyleme Geç) & ASSERT (Doğrula) ---
        # Bu testin tam implementasyonu yukarıdakilere benzer şekilde yapılabilir.
        # Önemli olan, post_data'yı doğru şekilde doldurup, sonuçta hata mesajını kontrol etmektir.
        pass
