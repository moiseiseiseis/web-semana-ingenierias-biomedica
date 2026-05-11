import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';

// --- DATOS DE PRUEBA (Sustituye esto por tu fetch a Flask luego) ---
const EVENTOS_MOCK = [
  {
    id: 1,
    titulo: "IA en el Diagnóstico Clínico",
    tipo: "Conferencia",
    ponente: "Dr. Julián García",
    fecha: "24/03/2026",
    imagen: "https://images.unsplash.com/photo-1576086213369-97a306d36557?auto=format&fit=crop&q=80&w=800",
    descripcion: "Explorando redes neuronales aplicadas a la detección temprana de patologías."
  },
  {
    id: 2,
    titulo: "Taller de Prótesis Robóticas",
    tipo: "Taller",
    ponente: "Mtra. Elena Ríos",
    fecha: "25/03/2026",
    imagen: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=800",
    descripcion: "Diseño y control de actuadores para extremidades superiores."
  }
];

const Home = () => {
  const [isPlaying, setIsPlaying] = useState(true);
  const videoRef = useRef(null);

  const toggleVideo = () => {
    if (videoRef.current) {
      isPlaying ? videoRef.current.pause() : videoRef.current.play();
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-gray-100 p-4 md:p-8 font-sans">
      
      {/* ===================== HERO SECTION ===================== */}
      <motion.section 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative h-[60vh] rounded-3xl overflow-hidden border border-white/10 shadow-2xl"
      >
        <video
          ref={videoRef}
          className="absolute inset-0 w-full h-full object-cover scale-105"
          autoPlay muted loop playsInline
        >
          <source src="/static/video/hero.mp4" type="video/mp4" />
        </video>
        
        {/* Overlay Gradiente */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-black/40 to-transparent" />

        <div className="absolute inset-0 p-8 flex flex-col justify-end max-w-4xl">
          <motion.span 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-yellow-500 font-mono text-sm tracking-widest uppercase mb-2"
          >
            Semana de Ingenierías 2026
          </motion.span>
          <h1 className="text-4xl md:text-6xl font-black mb-4 tracking-tighter">
            Ingeniería <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-yellow-600">Biomédica</span>
          </h1>
          <p className="text-gray-300 text-lg max-w-2xl mb-6">
            Conferencias de vanguardia, talleres prácticos y la comunidad científica más grande del centro universitario.
          </p>
          
          <div className="flex flex-wrap gap-4">
            <button className="px-8 py-3 bg-yellow-500 hover:bg-yellow-400 text-black font-bold rounded-full transition-all transform hover:scale-105 shadow-lg shadow-yellow-500/20">
              Registrarme ahora
            </button>
            <button onClick={toggleVideo} className="px-6 py-3 bg-white/10 hover:bg-white/20 backdrop-blur-md rounded-full border border-white/10 transition-all text-sm">
              {isPlaying ? 'Pausar Visual' : 'Reproducir Visual'}
            </button>
          </div>
        </div>
      </motion.section>

      {/* ===================== MAIN GRID ===================== */}
      <main className="mt-12 grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* COLUMNA IZQUIERDA: PROGRAMA */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between border-b border-white/5 pb-4">
            <h2 className="text-2xl font-bold">Programa de Eventos</h2>
            <span className="text-xs text-gray-500 uppercase tracking-widest">Desliza para ver más</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {EVENTOS_MOCK.map((ev, index) => (
              <motion.article 
                key={ev.id}
                whileHover={{ y: -5 }}
                className="group bg-white/[0.03] border border-white/10 rounded-2xl overflow-hidden hover:bg-white/[0.06] transition-all"
              >
                <div className="h-48 overflow-hidden">
                  <img src={ev.imagen} alt={ev.titulo} className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
                </div>
                <div className="p-6">
                  <div className="flex justify-between text-[10px] font-bold uppercase tracking-widest text-yellow-500 mb-2">
                    <span>{ev.tipo}</span>
                    <span className="text-gray-500">{ev.fecha}</span>
                  </div>
                  <h3 className="text-xl font-bold mb-2 group-hover:text-yellow-400 transition-colors">{ev.titulo}</h3>
                  <p className="text-gray-400 text-sm mb-4 line-clamp-2">{ev.descripcion}</p>
                  <div className="pt-4 border-t border-white/5 flex justify-between items-center">
                    <span className="text-xs italic text-gray-500">{ev.ponente}</span>
                    <button className="text-sm font-semibold text-yellow-500 hover:text-yellow-300">Detalles →</button>
                  </div>
                </div>
              </motion.article>
            ))}
          </div>
        </div>

        {/* COLUMNA DERECHA: ASIDE */}
        <aside className="space-y-6">
          <div className="sticky top-8 space-y-6">
            
            {/* CARD UBICACIÓN */}
            <div className="p-6 bg-gradient-to-br from-yellow-500/10 to-transparent border border-yellow-500/20 rounded-2xl">
              <h4 className="text-xs font-bold text-yellow-500 uppercase tracking-widest mb-4">Ubicación</h4>
              <p className="font-bold text-lg">Centro Universitario</p>
              <p className="text-gray-400 text-sm">Tlajomulco de Zúñiga, Jalisco.</p>
              <button className="mt-4 text-sm text-yellow-500 hover:underline">Abrir en Maps</button>
            </div>

            {/* CARD PASOS (WIZARD) */}
            <div className="p-6 bg-white/[0.03] border border-white/10 rounded-2xl">
              <h4 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">Registro en 3 pasos</h4>
              <ul className="space-y-4">
                {[
                  { n: 1, t: "Cuenta", d: "Usa tu código de alumno." },
                  { n: 2, t: "Equipo", d: "Opcional para talleres." },
                  { n: 3, t: "Confirmar", d: "Recibe tu código QR." }
                ].map(p => (
                  <li key={p.n} className="flex gap-4 items-start">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-yellow-500 text-black text-xs font-bold flex items-center justify-center">
                      {p.n}
                    </span>
                    <div>
                      <p className="text-sm font-bold">{p.t}</p>
                      <p className="text-xs text-gray-500">{p.d}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>

          </div>
        </aside>
      </main>
    </div>
  );
};

export default Home;