import React from 'react'

const ChatInput = () => {
  return (
    <div className="max-w-3xl mx-auto relative">
    {/* Glowing Background Effect */}
    <motion.div
      className="absolute -inset-3 bg-cyan-500/15 rounded-xl blur-2xl"
      animate={{
        scale: isFocused ? 1.1 : 1,
        opacity: isFocused ? 0.8 : 0.5
      }}
      transition={{
        duration: 0.3,
        ease: "easeInOut"
      }}
    />
    
    {/* Additional glow layers for more intensity */}
    <motion.div
      className="absolute -inset-3 bg-cyan-600/60 rounded-xl blur-3xl"
      animate={{
        scale: isFocused ? 1.15 : 1.05,
        opacity: isFocused ? 0.6 : 0.4
      }}
      transition={{
        duration: 0.3,
        ease: "easeInOut"
      }}
    />

    <div className="relative">
      <Textarea
        className="w-full min-h-[120px] bg-gray-900/90 border-gray-700/50 text-white placeholder:text-gray-400 text-lg p-6 rounded-lg relative z-10 backdrop-blur-sm resize-none focus:outline-cyan-400"
        placeholder="What would you like to build? Start typing or choose an example..."
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
      />
    </div>
  </div>
  )
}

export default ChatInput