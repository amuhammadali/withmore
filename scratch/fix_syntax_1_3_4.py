import os

# 1. Fix MiniApp.tsx
with open("frontend/src/miniapp/MiniApp.tsx", "r", encoding="utf-8") as f:
    app = f.read()

# Fix lookbooks in HomeScreen:
# Currently lookbooks state was placed in App() instead of HomeScreen.
# Let's remove the misplaced lookbooks state from App()
misplaced_lookbook_state = '''  const [lookbooks, setLookbooks] = useState<any[]>([]);
  const [addingBundleId, setAddingBundleId] = useState<number | null>(null);

  useEffect(() => {
    shopFetch("/api/shop/lookbooks")
      .then((data) => {
        if (Array.isArray(data)) setLookbooks(data);
      })
      .catch(() => {});
  }, []);

  const handleAddBundle = async (bid: number) => {
    setAddingBundleId(bid);
    try {
      const res = await shopFetch(`/api/shop/lookbooks/${bid}/add-bundle`, {
        method: "POST",
      });
      toast(res.message || "To'liq obraz savatingizga qo'shildi!", "success");
    } catch (e: any) {
      toast(e.message || "Xatolik yuz berdi", "error");
    } finally {
      setAddingBundleId(null);
    }
  };'''

if misplaced_lookbook_state in app:
    app = app.replace(misplaced_lookbook_state, "")

# Now add lookbooks state inside HomeScreen:
homescreen_target = '''function HomeScreen({
  content,
  categories,
  customerName,
  favIds,
  onToggleFav,
}: {
  content: any;
  categories: any[];
  customerName?: string;
  favIds: number[];
  onToggleFav: (id: number) => void;
}) {
  const { lang, t } = useLang();
  const [featured, setFeatured] = useState<any[]>([]);'''

homescreen_replacement = '''function HomeScreen({
  content,
  categories,
  customerName,
  favIds,
  onToggleFav,
}: {
  content: any;
  categories: any[];
  customerName?: string;
  favIds: number[];
  onToggleFav: (id: number) => void;
}) {
  const { lang, t } = useLang();
  const { toast } = useToast();
  const [featured, setFeatured] = useState<any[]>([]);
  const [lookbooks, setLookbooks] = useState<any[]>([]);
  const [addingBundleId, setAddingBundleId] = useState<number | null>(null);

  useEffect(() => {
    shopFetch("/api/shop/lookbooks")
      .then((data) => {
        if (Array.isArray(data)) setLookbooks(data);
      })
      .catch(() => {});
  }, []);

  const handleAddBundle = async (bid: number) => {
    setAddingBundleId(bid);
    try {
      const res = await shopFetch(`/api/shop/lookbooks/${bid}/add-bundle`, {
        method: "POST",
      });
      toast(res.message || "To'liq obraz savatingizga qo'shildi!", "success");
    } catch (e: any) {
      toast(e.message || "Xatolik yuz berdi", "error");
    } finally {
      setAddingBundleId(null);
    }
  };'''

if homescreen_target in app:
    app = app.replace(homescreen_target, homescreen_replacement)

# Fix Referral Card position:
# Cut referral_ui_card from CartScreen and put it into AboutScreen
ref_start = '{/* ---------------- GENTLEMEN REFERRAL CLUB CARD ---------------- */}'
ref_end = '</section>\n'
p1 = app.find(ref_start)
if p1 != -1:
    p2 = app.find(ref_end, p1) + len(ref_end)
    ref_card_text = app[p1:p2]
    app = app[:p1] + app[p2:] # removed from CartScreen

    # Now put it into AboutScreen right above FAQ or Direct Support Banner
    about_target = '{/* Brand Story */}'
    about_pos = app.find(about_target)
    if about_pos != -1:
        # Put it after Brand Story
        insert_marker = '{/* Customer Orders */}'
        ins_pos = app.find(insert_marker, about_pos)
        if ins_pos != -1:
            app = app[:ins_pos] + ref_card_text + '\n      ' + app[ins_pos:]

with open("frontend/src/miniapp/MiniApp.tsx", "w", encoding="utf-8") as f:
    f.write(app)
print("MiniApp.tsx adjusted perfectly!")


# 2. Fix AdminPages2.tsx
with open("frontend/src/admin/AdminPages2.tsx", "r", encoding="utf-8") as f:
    adm = f.read()

# Remove duplicate const { t } = useLang(); and toast in MarketingPage
# Check lines where duplicate t and toast appear
dup_t_toast = '''  const { t } = useLang();
  const { toast } = useToast();
  const [rows, setRows] = useState<any[]>([]);'''

replacement_t_toast = '''  const [rows, setRows] = useState<any[]>([]);'''

if dup_t_toast in adm:
    adm = adm.replace(dup_t_toast, replacement_t_toast, 1)

with open("frontend/src/admin/AdminPages2.tsx", "w", encoding="utf-8") as f:
    f.write(adm)
print("AdminPages2.tsx adjusted perfectly!")

