import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Translation resources
const resources = {
  en: {
    translation: {
      language:"English",
      code:'en',
      avatarVoice:{
        voice_id: '76955c80188a4c149df169b5dc9e1a3a',
        language:"English" 
      },
      reportLanguage:"English",
      hero: {
        titlePart1: "Find Your",
        titlePart2:'Dream Property',
        titlePart3:'with Ease',
        subtitle: "Let our Real Estate AI Assistant guide you to your perfect space.",
      },
      textArea:{
        placeholder:'Hi, I’m your smart real estate companion, here to find your perfect property and answer all your real estate questions!',
        sendBtn:'Send',
        newChatBtn:'New Chat',
        mapBtn:"Map"
      },
      establishConnection:"Connect to AI Avatar",
      startConversation:"Start Conversation",
      report: "Report",
      hideReport: "Hide Report",
      reportHeading: "Please select a property to generate a report",
      mapView:"Map View",
      examples: [
       
          {
            exampleText: "🏠 Nearby properties",
            prompt: "Please show me a list of properties available for sale or rent near my current location."
          },
          {
            exampleText: "💰 Budget homes",
            prompt: "Can you help me find homes that are within my specified budget range and preferred location?"
          },
          {
            exampleText: "🌟 Popular areas",
            prompt: "I'd like to explore popular neighborhoods in the city to consider for buying or renting a home."
          },
          {
            exampleText: "🏡 Luxury villas",
            prompt: "Show me a collection of luxury villas available for purchase or rent in high-end neighborhoods."
          },
          {
            exampleText: "🏢 Commercial spaces",
            prompt: "I’m looking for commercial spaces nearby that are suitable for offices or retail stores."
          },
          {
            exampleText: "🌊 Waterfront homes",
            prompt: "Can you provide options for waterfront properties available for sale or rent in my area?"
          }
     
      ],
      introMessage:'Hi, I’m your smart real estate companion, here to find your perfect property and answer all your real estate questions'
    },
  },
  ar: {
    translation: {
      language:"العربية",
      code:'ar',
      avatarVoice:{
        voice_id: "02bec3b4cb514722a84e4e18d596fddf",
        language: "Arabic" 
      },
      reportLanguage:"Arabic",
      report: "تقرير",
      hideReport: "إخفاء التقرير",
      reportHeading: "حدد عقارًا لإنشاء التقرير",
      establishConnection:"اتصل بالذكاء الاصطناعي المجسم",
      startConversation:"ابدأ المحادثة",
      mapView:"عرض الخريطة",
      hero: {
        titlePart1: "ابحث عن",
        titlePart2: "عقار أحلامك",
        titlePart3: "بسهولة",
        subtitle: "دع مساعد العقارات الذكي الخاص بنا يوجهك إلى مساحتك المثالية.",
      },
      textArea:{
        placeholder: "مرحباً، أنا رفيقك الذكي في العقارات، هنا لأساعدك في العثور على العقار المثالي والإجابة على جميع أسئلتك العقارية!",
        sendBtn: "إرسال",
        newChatBtn: "دردشة جديدة",
        mapBtn:'رسم خريطة'
      },
      examples: [
       
          {
            exampleText: "🏠 عقارات قريبة",
            prompt: "يرجى عرض قائمة بالعقارات المتاحة للبيع أو الإيجار بالقرب من موقعي الحالي."
          },
          {
            exampleText: "💰 منازل اقتصادية",
            prompt: "هل يمكنك مساعدتي في العثور على منازل ضمن النطاق السعري المحدد والموقع المفضل لدي؟"
          },
          {
            exampleText: "🌟 مناطق مشهورة",
            prompt: "أود استكشاف الأحياء المشهورة في المدينة للنظر في شراء أو استئجار منزل."
          },
          {
            exampleText: "🏡 فلل فاخرة",
            prompt: "اعرض لي مجموعة من الفلل الفاخرة المتاحة للشراء أو الإيجار في الأحياء الراقية."
          },
          {
            exampleText: "🏢 مساحات تجارية",
            prompt: "أبحث عن مساحات تجارية قريبة تصلح للمكاتب أو المتاجر."
          },
          {
            exampleText: "🌊 منازل على الواجهة البحرية",
            prompt: "هل يمكنك تقديم خيارات للعقارات المطلة على الواجهة البحرية المتاحة للبيع أو الإيجار في منطقتي؟"
          }
     
      ],
      introMessage: "مرحباً، أنا رفيقك الذكي في العقارات، هنا لأساعدك في العثور على العقار المثالي والإجابة على جميع أسئلتك العقارية"
    },
  },

};

i18n.use(initReactI18next).init({
  resources,
  lng: "en", // Default language
  fallbackLng: "en", // Fallback language
  interpolation: {
    escapeValue: false, // React already escapes values to prevent XSS
  },
});

export default i18n;
