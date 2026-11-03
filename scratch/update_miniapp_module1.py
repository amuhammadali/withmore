import os
import re

print("Starting MiniApp.tsx Module 1 updates...")

miniapp_path = "frontend/src/miniapp/MiniApp.tsx"
with open(miniapp_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. In ProductScreen: Add fitting modal state
product_state_target = '''  const [revCity, setRevCity] = useState("Samarqand");
  const [revText, setRevText] = useState("");
  const [revSubmitting, setRevSubmitting] = useState(false);'''

product_state_replacement = product_state_target + '''
  // Fitting appointment state
  const [showFittingModal, setShowFittingModal] = useState(false);
  const [fittingDate, setFittingDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    return d.toISOString().split("T")[0];
  });
  const [fittingTime, setFittingTime] = useState("15:00 - 16:00");
  const [fittingName, setFittingName] = useState("");
  const [fittingPhone, setFittingPhone] = useState("+998");
  const [fittingNotes, setFittingNotes] = useState("");
  const [fittingHeight, setFittingHeight] = useState("");
  const [fittingWeight, setFittingWeight] = useState("");
  const [fittingFitPref, setFittingFitPref] = useState("regular");
  const [fittingSubmitting, setFittingSubmitting] = useState(false);

  useEffect(() => {
    // Preload measurements if customer has them saved
    shopFetch("/api/shop/measurements")
      .then((m) => {
        if (m) {
          if (m.height_cm) setFittingHeight(String(m.height_cm));
          if (m.weight_kg) setFittingWeight(String(m.weight_kg));
          if (m.fit_preference) setFittingFitPref(m.fit_preference);
        }
      })
      .catch(() => {});
  }, []);

  const handleBookFitting = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fittingName.trim() || fittingPhone.length < 9) {
      toast("Iltimos, ismingiz va telefon raqamingizni to'liq kiriting", "error");
      return;
    }
    setFittingSubmitting(true);
    try {
      const res = await shopFetch("/api/shop/fitting", {
        method: "POST",
        body: JSON.stringify({
          customer_name: fittingName.trim(),
          customer_phone: fittingPhone.trim(),
          appointment_date: fittingDate,
          appointment_time: fittingTime,
          product_id: product?.id,
          notes: fittingNotes.trim() || undefined,
          height_cm: fittingHeight ? Number(fittingHeight) : undefined,
          weight_kg: fittingWeight ? Number(fittingWeight) : undefined,
          fit_preference: fittingFitPref || undefined,
        }),
      });
      toast(res.message || "Primerka muvaffaqiyatli bron qilindi! Atelyeda kutamiz.", "success");
      setShowFittingModal(false);
    } catch (err: any) {
      toast(err.message || "Xatolik yuz berdi", "error");
    } finally {
      setFittingSubmitting(false);
    }
  };'''

if product_state_target in code and 'showFittingModal' not in code:
    code = code.replace(product_state_target, product_state_replacement)

# 2. Add Fitting Button in ProductScreen
fitting_btn_target = '''          {/* 1-Click Quick Order Button */}
          {selectedVariant && (
            <div className="mt-2.5">
              <button
                type="button"
                onClick={() => setShowQuickModal(true)}'''

fitting_btn_replacement = '''          {/* Atelier Bespoke Fitting Button */}
          <div className="mt-2.5">
            <button
              type="button"
              onClick={() => setShowFittingModal(true)}
              className="flex h-12 w-full items-center justify-center gap-2 rounded-2xl border-2 border-[#172641] bg-white text-[11px] font-bold uppercase tracking-[.14em] text-[#172641] shadow-[0_4px_14px_rgba(23,38,65,0.08)] hover:bg-[#172641] hover:text-[#f4efe5] hover:shadow-[0_6px_20px_rgba(23,38,65,0.2)] hover:-translate-y-0.5 transition-all duration-200 active:scale-[.98] cursor-pointer"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
              </svg>
              <span>Atelyeda kiyib ko‘rish (Primerka bron)</span>
            </button>
            <div className="mt-1 text-center text-[10px] text-slate-900/60 font-medium">
              Bespoke ustasi bilan o‘lcham olish va qomatga moslashtirish bepul
            </div>
          </div>

          {/* 1-Click Quick Order Button */}
          {selectedVariant && (
            <div className="mt-2.5">
              <button
                type="button"
                onClick={() => setShowQuickModal(true)}'''

if fitting_btn_target in code and 'Atelyeda kiyib ko‘rish (Primerka bron)' not in code:
    code = code.replace(fitting_btn_target, fitting_btn_replacement)

# 3. Add Fitting Modal in ProductScreen
fitting_modal_code = '''          {/* Atelier Fitting Appointment Modal */}
          {showFittingModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm overflow-y-auto">
              <div className="w-full max-w-sm rounded-2xl border border-border bg-[#faf8f3] p-5 shadow-2xl text-slate-900 space-y-4 rise-in my-6 max-h-[92vh] overflow-y-auto">
                <div className="flex items-center justify-between border-b border-[#172641]/10 pb-3">
                  <div>
                    <span className="text-[9px] font-bold uppercase tracking-[.2em] text-[#a4814d]">
                      WITHMORE ATELIER
                    </span>
                    <h3 className="font-display text-lg font-bold text-[#172641]">
                      Atelyeda kiyib ko‘rish (Primerka)
                    </h3>
                  </div>
                  <button
                    type="button"
                    onClick={() => setShowFittingModal(false)}
                    className="rounded-lg p-1 text-slate-500 hover:text-slate-900 cursor-pointer"
                  >
                    ✕
                  </button>
                </div>

                <div className="rounded-xl border border-[#c5a676]/30 bg-[#fbf8f0] p-3 text-xs text-slate-800">
                  <div className="font-bold text-[#172641] flex items-center gap-1.5">
                    <span>📍</span>
                    <span>Toshkent sh., Withmore Sartorial Atelyesi</span>
                  </div>
                  <div className="mt-1 text-[11px] text-slate-600">
                    Tanlangan kostyum siz uchun alohida tayyorlab qo‘yiladi. Mutaxassis bichuvchi qomatingizga qarab to‘g‘rilaydi.
                  </div>
                </div>

                <form onSubmit={handleBookFitting} className="space-y-3">
                  <div>
                    <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-700">
                      Sana *
                    </label>
                    <input
                      type="date"
                      required
                      value={fittingDate}
                      onChange={(e) => setFittingDate(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-[#172641]/20 bg-white p-2.5 text-xs text-slate-900"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-700">
                      Qulay vaqt oralig‘i *
                    </label>
                    <select
                      value={fittingTime}
                      onChange={(e) => setFittingTime(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-[#172641]/20 bg-white p-2.5 text-xs text-slate-900 font-medium"
                    >
                      <option value="11:00 - 12:00">11:00 - 12:00 (Ertalabki seans)</option>
                      <option value="13:00 - 14:00">13:00 - 14:00 (Tushlik vaqti)</option>
                      <option value="15:00 - 16:00">15:00 - 16:00 (Kunduzgi seans)</option>
                      <option value="17:00 - 18:00">17:00 - 18:00 (Kechki seans)</option>
                      <option value="19:00 - 20:00">19:00 - 20:00 (Ishdan keyin)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-700">
                      Ism va familiyangiz *
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="Masalan: Sardor Aliyev"
                      value={fittingName}
                      onChange={(e) => setFittingName(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-[#172641]/20 bg-white p-2.5 text-xs text-slate-900"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-700">
                      Telefon raqamingiz *
                    </label>
                    <input
                      type="tel"
                      required
                      placeholder="+998 90 123 45 67"
                      value={fittingPhone}
                      onChange={(e) => setFittingPhone(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-[#172641]/20 bg-white p-2.5 text-xs text-slate-900"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-700">
                        Bo‘yingiz (sm)
                      </label>
                      <input
                        type="number"
                        placeholder="178"
                        value={fittingHeight}
                        onChange={(e) => setFittingHeight(e.target.value)}
                        className="mt-1 w-full rounded-xl border border-[#172641]/20 bg-white p-2 text-xs text-slate-900"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-700">
                        Vazningiz (kg)
                      </label>
                      <input
                        type="number"
                        placeholder="76"
                        value={fittingWeight}
                        onChange={(e) => setFittingWeight(e.target.value)}
                        className="mt-1 w-full rounded-xl border border-[#172641]/20 bg-white p-2 text-xs text-slate-900"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-700">
                      Qo‘shimcha istak yoki izoh
                    </label>
                    <textarea
                      rows={2}
                      placeholder="Masalan: Shim balandligini qisqartirish kerak..."
                      value={fittingNotes}
                      onChange={(e) => setFittingNotes(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-[#172641]/20 bg-white p-2 text-xs text-slate-900"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={fittingSubmitting}
                    className="w-full rounded-xl bg-[#172641] py-3 text-xs font-bold uppercase tracking-wider text-[#faf7f2] shadow-md hover:bg-[#23385e] transition cursor-pointer"
                  >
                    {fittingSubmitting ? "Bron qilinmoqda..." : "Primerkani bron qilish"}
                  </button>
                </form>
              </div>
            </div>
          )}
'''

if '{showQuickModal && (' in code and '{showFittingModal && (' not in code:
    code = code.replace(
        '{showQuickModal && (',
        fitting_modal_code + '\n          {showQuickModal && ('
    )

# 4. In AboutScreen: Add "Bespoke Qomat Pasporti" and "Atelye Primerkalari"
about_state_target = '''  const [favProducts, setFavProducts] = useState<any[]>([]);
  const [openFaq, setOpenFaq] = useState<number | null>(0);'''

about_state_replacement = about_state_target + '''
  // Sartorial Measurements Profile
  const [measurements, setMeasurements] = useState<any>(null);
  const [loadingMeasurements, setLoadingMeasurements] = useState(false);
  const [showEditMeasurements, setShowEditMeasurements] = useState(false);
  const [editM, setEditM] = useState({
    height_cm: "",
    weight_kg: "",
    suit_size: "",
    collar_cm: "",
    shoe_size: "",
    fit_preference: "regular",
  });
  const [savingM, setSavingM] = useState(false);

  // Fittings history
  const [myFittings, setMyFittings] = useState<any[]>([]);

  useEffect(() => {
    setLoadingMeasurements(true);
    shopFetch("/api/shop/measurements")
      .then((res) => {
        if (res) {
          setMeasurements(res);
          setEditM({
            height_cm: res.height_cm ? String(res.height_cm) : "",
            weight_kg: res.weight_kg ? String(res.weight_kg) : "",
            suit_size: res.suit_size || "",
            collar_cm: res.collar_cm ? String(res.collar_cm) : "",
            shoe_size: res.shoe_size || "",
            fit_preference: res.fit_preference || "regular",
          });
        }
      })
      .catch(() => {})
      .finally(() => setLoadingMeasurements(false));

    shopFetch("/api/shop/fitting")
      .then((res) => {
        if (Array.isArray(res)) setMyFittings(res);
      })
      .catch(() => {});
  }, []);

  const handleSaveMeasurements = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingM(true);
    try {
      const payload = {
        height_cm: editM.height_cm ? Number(editM.height_cm) : null,
        weight_kg: editM.weight_kg ? Number(editM.weight_kg) : null,
        suit_size: editM.suit_size || null,
        collar_cm: editM.collar_cm ? Number(editM.collar_cm) : null,
        shoe_size: editM.shoe_size || null,
        fit_preference: editM.fit_preference || "regular",
      };
      await shopFetch("/api/shop/measurements", {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      setMeasurements(payload);
      setShowEditMeasurements(false);
      toast("Qomat pasportingiz muvaffaqiyatli saqlandi!", "success");
    } catch (err: any) {
      toast(err.message || "Saqlashda xatolik yuz berdi", "error");
    } finally {
      setSavingM(false);
    }
  };'''

if about_state_target in code and 'measurements, setMeasurements' not in code:
    code = code.replace(about_state_target, about_state_replacement)

# 5. Add Sartorial Passport and Fittings section in AboutScreen render
about_orders_target = '''      {/* Customer Orders */}
      {myOrders.length > 0 && ('''

sartorial_sections = '''      {/* ---------------- BESPOKE QOMAT PASPORTI (SARTORIAL PROFILE) ---------------- */}
      <section className="border-t border-[#172641]/15 pt-5 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-[9px] font-bold uppercase tracking-[.2em] text-[#a4814d]">
              EXCLUSIVE BESPOKE FIT
            </span>
            <h2 className="font-display text-[22px] text-slate-900">
              Raqamli Qomat Pasporti
            </h2>
          </div>
          <button
            type="button"
            onClick={() => setShowEditMeasurements(true)}
            className="rounded-xl border border-[#c5a676] bg-[#faf5ea] hover:bg-[#c5a676] hover:text-white px-3 py-1.5 text-xs font-bold text-[#172641] transition cursor-pointer"
          >
            {measurements ? "Tahrirlash" : "+ O'lchamlarni kiritish"}
          </button>
        </div>

        <div className="rounded-2xl border border-[#c5a676]/40 bg-gradient-to-br from-[#fbf8f0] via-[#ffffff] to-[#faf5ea] p-4 shadow-sm space-y-3">
          <div className="text-xs text-slate-600">
            Shaxsiy qomat ko‘rsatkichlaringiz saqlanadi. Har qanday kostyum va ko‘ylak sizga mukammal yarashishi uchun atelye ustasi ushbu raqamlar asosida ishlaydi.
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-1">
            <div className="rounded-xl border border-border/80 bg-white p-2.5 text-center">
              <span className="text-[10px] font-bold uppercase text-slate-400 block">Bo‘yingiz</span>
              <span className="text-sm font-extrabold text-[#172641]">
                {measurements?.height_cm ? `${measurements.height_cm} sm` : "—"}
              </span>
            </div>

            <div className="rounded-xl border border-border/80 bg-white p-2.5 text-center">
              <span className="text-[10px] font-bold uppercase text-slate-400 block">Vazningiz</span>
              <span className="text-sm font-extrabold text-[#172641]">
                {measurements?.weight_kg ? `${measurements.weight_kg} kg` : "—"}
              </span>
            </div>

            <div className="rounded-xl border border-border/80 bg-white p-2.5 text-center">
              <span className="text-[10px] font-bold uppercase text-slate-400 block">Kostyum o‘lchami</span>
              <span className="text-sm font-extrabold text-[#172641]">
                {measurements?.suit_size || "—"}
              </span>
            </div>

            <div className="rounded-xl border border-border/80 bg-white p-2.5 text-center">
              <span className="text-[10px] font-bold uppercase text-slate-400 block">Yoqa aylanasi</span>
              <span className="text-sm font-extrabold text-[#172641]">
                {measurements?.collar_cm ? `${measurements.collar_cm} sm` : "—"}
              </span>
            </div>

            <div className="rounded-xl border border-border/80 bg-white p-2.5 text-center">
              <span className="text-[10px] font-bold uppercase text-slate-400 block">Poyabzal o‘lchami</span>
              <span className="text-sm font-extrabold text-[#172641]">
                {measurements?.shoe_size || "—"}
              </span>
            </div>

            <div className="rounded-xl border border-border/80 bg-white p-2.5 text-center">
              <span className="text-[10px] font-bold uppercase text-slate-400 block">Bichiq uslubi</span>
              <span className="text-sm font-extrabold text-[#c5a676] capitalize">
                {measurements?.fit_preference || "Regular"}
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Edit Measurements Modal */}
      {showEditMeasurements && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm overflow-y-auto">
          <div className="w-full max-w-sm rounded-2xl border border-border bg-[#faf8f3] p-5 shadow-2xl text-slate-900 space-y-4 rise-in my-6">
            <div className="flex items-center justify-between border-b border-[#172641]/10 pb-3">
              <div>
                <span className="text-[9px] font-bold uppercase tracking-[.2em] text-[#a4814d]">
                  WITHMORE PASPORT
                </span>
                <h3 className="font-display text-lg font-bold text-[#172641]">
                  Qomat Pasportini to‘ldirish
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setShowEditMeasurements(false)}
                className="rounded-lg p-1 text-slate-500 hover:text-slate-900 cursor-pointer"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSaveMeasurements} className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-700">
                    Bo‘y (sm)
                  </label>
                  <input
                    type="number"
                    placeholder="178"
                    value={editM.height_cm}
                    onChange={(e) => setEditM({ ...editM, height_cm: e.target.value })}
                    className="mt-1 w-full rounded-xl border border-[#172641]/20 bg-white p-2 text-xs text-slate-900"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-700">
                    Vazn (kg)
                  </label>
                  <input
                    type="number"
                    placeholder="76"
                    value={editM.weight_kg}
                    onChange={(e) => setEditM({ ...editM, weight_kg: e.target.value })}
                    className="mt-1 w-full rounded-xl border border-[#172641]/20 bg-white p-2 text-xs text-slate-900"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-700">
                    Kostyum (masalan: 50)
                  </label>
                  <input
                    type="text"
                    placeholder="48, 50, 52..."
                    value={editM.suit_size}
                    onChange={(e) => setEditM({ ...editM, suit_size: e.target.value })}
                    className="mt-1 w-full rounded-xl border border-[#172641]/20 bg-white p-2 text-xs text-slate-900"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-700">
                    Yoqa (sm)
                  </label>
                  <input
                    type="number"
                    placeholder="41"
                    value={editM.collar_cm}
                    onChange={(e) => setEditM({ ...editM, collar_cm: e.target.value })}
                    className="mt-1 w-full rounded-xl border border-[#172641]/20 bg-white p-2 text-xs text-slate-900"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-700">
                    Poyabzal
                  </label>
                  <input
                    type="text"
                    placeholder="42, 43..."
                    value={editM.shoe_size}
                    onChange={(e) => setEditM({ ...editM, shoe_size: e.target.value })}
                    className="mt-1 w-full rounded-xl border border-[#172641]/20 bg-white p-2 text-xs text-slate-900"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-700">
                    Bichiq afzalligi
                  </label>
                  <select
                    value={editM.fit_preference}
                    onChange={(e) => setEditM({ ...editM, fit_preference: e.target.value })}
                    className="mt-1 w-full rounded-xl border border-[#172641]/20 bg-white p-2 text-xs text-slate-900 font-semibold"
                  >
                    <option value="slim">Slim Fit (Qomatga yopishgan)</option>
                    <option value="regular">Regular Fit (Klassik erkin)</option>
                    <option value="relaxed">Relaxed (Erkin / Keng)</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                disabled={savingM}
                className="w-full rounded-xl bg-[#172641] py-3 text-xs font-bold uppercase tracking-wider text-[#faf7f2] shadow-md hover:bg-[#23385e] transition cursor-pointer"
              >
                {savingM ? "Saqlanmoqda..." : "Pasportni saqlash"}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* ---------------- REJALASHTIRILGAN ATELYE PRIMERKALARI ---------------- */}
      {myFittings.length > 0 && (
        <section className="border-t border-[#172641]/15 pt-5 space-y-3">
          <h2 className="font-display text-[22px] text-slate-900">
            Atelye Primerkalari
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {myFittings.map((fit) => (
              <div
                key={fit.id}
                className="rounded-2xl border border-[#172641]/15 bg-[#fbf8f2] p-3.5 space-y-1.5 text-slate-900"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-extrabold text-[#172641]">
                    📅 {fit.appointment_date}
                  </span>
                  <span
                    className={`rounded-full px-2 py-0.5 text-[9px] font-bold uppercase ${
                      fit.status === "confirmed"
                        ? "bg-blue-100 text-[#172641]"
                        : fit.status === "completed"
                        ? "bg-emerald-100 text-emerald-800"
                        : "bg-amber-100 text-amber-800"
                    }`}
                  >
                    {fit.status}
                  </span>
                </div>
                <div className="text-[11px] text-slate-600">
                  ⏰ Vaqt: <b>{fit.appointment_time || "Belgilanmagan"}</b>
                </div>
                <div className="text-[10px] text-slate-500">
                  📍 Withmore Bespoke Atelyesi (Toshkent)
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
'''

if about_orders_target in code and 'Raqamli Qomat Pasporti' not in code:
    code = code.replace(about_orders_target, sartorial_sections + '\n' + about_orders_target)

with open(miniapp_path, "w", encoding="utf-8") as f:
    f.write(code)

print("MiniApp.tsx updated successfully!")

